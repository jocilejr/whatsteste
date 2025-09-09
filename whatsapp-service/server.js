const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys')
const express = require('express')
const cors = require('cors')
const axios = require('axios')
const fs = require('fs-extra')
const path = require('path')

const app = express()
app.use(cors())
app.use(express.json())

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8001'
const PORT = process.env.PORT || 3001

let sock = null
let qrCode = null
let isConnected = false
let connectedUser = null

// Ensure auth directory exists
const authDir = path.join(__dirname, 'auth_info')
fs.ensureDirSync(authDir)

async function initWhatsApp() {
    try {
        console.log('Initializing WhatsApp connection...')
        const { state, saveCreds } = await useMultiFileAuthState(authDir)

        sock = makeWASocket({
            auth: state,
            printQRInTerminal: false,
            browser: ['WhatsFlow Bot', 'Chrome', '1.0.0'],
            markOnlineOnConnect: false
        })

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update

            if (qr) {
                qrCode = qr
                console.log('QR Code generated')
                // Notify FastAPI about QR code
                try {
                    await axios.post(`${FASTAPI_URL}/api/whatsapp/qr-update`, { qr })
                } catch (error) {
                    console.log('Failed to notify FastAPI about QR:', error.message)
                }
            }

            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut
                console.log('Connection closed due to ', lastDisconnect?.error, ', reconnecting ', shouldReconnect)

                isConnected = false
                connectedUser = null
                
                if (shouldReconnect) {
                    setTimeout(initWhatsApp, 5000)
                }
            } else if (connection === 'open') {
                console.log('WhatsApp connected successfully!')
                qrCode = null
                isConnected = true
                connectedUser = sock.user
                
                // Notify FastAPI about connection
                try {
                    await axios.post(`${FASTAPI_URL}/api/whatsapp/connection-update`, {
                        connected: true,
                        user: connectedUser
                    })
                } catch (error) {
                    console.log('Failed to notify FastAPI about connection:', error.message)
                }
            }
        })

        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type === 'notify') {
                for (const message of messages) {
                    if (!message.key.fromMe && message.message) {
                        await handleIncomingMessage(message)
                    }
                }
            }
        })

        sock.ev.on('creds.update', saveCreds)

    } catch (error) {
        console.error('WhatsApp initialization error:', error)
        setTimeout(initWhatsApp, 10000)
    }
}

async function handleIncomingMessage(message) {
    try {
        const phoneNumber = message.key.remoteJid.replace('@s.whatsapp.net', '')
        const messageText = message.message.conversation ||
                           message.message.extendedTextMessage?.text || ''
        
        const pushName = message.pushName || 'Unknown'
        
        console.log(`Received message from ${pushName} (${phoneNumber}): ${messageText}`)

        // Forward message to FastAPI for processing
        const response = await axios.post(`${FASTAPI_URL}/api/whatsapp/message`, {
            phone_number: phoneNumber,
            message: messageText,
            message_id: message.key.id,
            timestamp: message.messageTimestamp,
            push_name: pushName
        })

        // Send response back to WhatsApp if FastAPI returns one
        if (response.data.reply) {
            await sendMessage(phoneNumber, response.data.reply)
        }

    } catch (error) {
        console.error('Error handling incoming message:', error)
    }
}

async function sendMessage(phoneNumber, text) {
    try {
        if (!sock || !isConnected) {
            throw new Error('WhatsApp not connected')
        }

        const jid = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`
        await sock.sendMessage(jid, { text })
        console.log(`Message sent to ${phoneNumber}: ${text}`)
        return { success: true }

    } catch (error) {
        console.error('Error sending message:', error)
        return { success: false, error: error.message }
    }
}

// REST API endpoints
app.get('/qr', async (req, res) => {
    try {
        res.json({ qr: qrCode || null })
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

app.post('/send', async (req, res) => {
    const { phone_number, message } = req.body
    const result = await sendMessage(phone_number, message)
    res.json(result)
})

app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        user: connectedUser,
        hasQR: !!qrCode
    })
})

app.listen(PORT, () => {
    console.log(`WhatsApp service running on port ${PORT}`)
    console.log(`FastAPI URL: ${FASTAPI_URL}`)
    initWhatsApp()
})

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Shutting down gracefully...')
    if (sock) {
        sock.end()
    }
    process.exit(0)
})