#!/usr/bin/env python3
"""
WhatsFlow Real - Versão com Baileys REAL
Sistema de Automação WhatsApp com conexão verdadeira

Requisitos: Python 3 + Node.js (para Baileys)
Instalação: python3 whatsflow-real.py
Acesso: http://localhost:8888
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import os
import subprocess
import sys
import threading
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging
from typing import Set, Dict, Any
import asyncio
import base64

# Try to import websockets, fallback gracefully if not available
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️ WebSocket não disponível - executando sem tempo real")

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8889
BAILEYS_PORT = 3002

# Brazil timezone
BR_TZ = ZoneInfo("America/Sao_Paulo")
BAILEYS_URL = os.getenv("BAILEYS_URL", f"http://127.0.0.1:{BAILEYS_PORT}")
WEBSOCKET_PORT = 8890

# WebSocket clients management
if WEBSOCKETS_AVAILABLE:
    websocket_clients: Set[websockets.WebSocketServerProtocol] = set()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML da aplicação (mesmo do Pure, mas com conexão real)
HTML_APP = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow Real - Sistema Profissional</title>
    <style>
        /* Professional WhatsFlow Design - Ultra Modern */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #128c7e;
            --primary-dark: #075e54;
            --primary-light: #25d366;
            --bg-primary: #f0f2f5;
            --bg-secondary: #ffffff;
            --bg-chat: #e5ddd5;
            --text-primary: #111b21;
            --text-secondary: #667781;
            --border: #e9edef;
            --shadow: 0 1px 3px rgba(11,20,26,.13);
            --shadow-lg: 0 2px 10px rgba(11,20,26,.2);
            --gradient-primary: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
            --gradient-success: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8fafc;
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 0 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Add professional spacing */
        body {
            margin: 0;
            padding: 0;
            background: #f8f9fa;
        }
        
        /* Navigation improvements */
        .nav {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
            padding: 8px;
        }
        
        /* Sections with professional spacing */
        .section {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 0 0 20px 0;
            min-height: calc(100vh - 200px);
        }
        
        /* Messages section improvements */
        #messages.section {
            height: calc(100vh - 120px);
            max-height: calc(100vh - 120px);
            margin: 0;
        }
        
        /* Messages Section - Professional WhatsApp-like Design */
        .messages-section {
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #f0f2f5;
        }
        
        .messages-header {
            background: white;
            padding: 20px 24px;
            border-bottom: 1px solid #e9edef;
            box-shadow: 0 1px 3px rgba(11,20,26,.1);
        }
        
        .messages-header h2 {
            margin: 0 0 12px 0;
            font-size: 1.4rem;
            font-weight: 600;
            color: #111b21;
        }
        
        .instance-selector {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .instance-selector label {
            font-size: 0.9rem;
            color: #667781;
            font-weight: 500;
        }
        
        .instance-selector select {
            flex: 1;
            max-width: 250px;
            padding: 8px 12px;
            border: 1px solid #d1d7db;
            border-radius: 8px;
            background: white;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        
        .instance-selector select:focus {
            outline: none;
            border-color: #00a884;
            box-shadow: 0 0 0 2px rgba(0,168,132,0.1);
        }
        
        .messages-content {
            flex: 1;
            display: flex;
            min-height: 0;
            background: linear-gradient(135deg, #f8fafe 0%, #f0f7f4 100%);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(16, 24, 40, 0.06);
            margin: 0 8px 8px 8px;
        }
        
        /* Conversations Panel - Ultra Professional Design */
        .conversations-panel {
            width: 380px;
            background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
            border-right: 1px solid #e3e8ed;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        
        .conversations-panel::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 1px;
            height: 100%;
            background: linear-gradient(180deg, 
                rgba(18, 140, 126, 0.1) 0%, 
                rgba(18, 140, 126, 0.05) 50%, 
                rgba(18, 140, 126, 0.1) 100%);
        }
        
        .search-bar {
            padding: 20px 16px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-bottom: 1px solid #e3e8ed;
            position: relative;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05);
        }
        
        .search-input {
            width: 100%;
            padding: 14px 20px 14px 48px;
            border: 2px solid transparent;
            border-radius: 28px;
            background: #ffffff;
            font-size: 0.95rem;
            color: #1c2025;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            box-shadow: 0 2px 8px rgba(16, 24, 40, 0.08);
            font-weight: 400;
            letter-spacing: 0.01em;
        }
        
        .search-input::placeholder {
            color: #6c737f;
            font-weight: 400;
        }
        
        .search-input:focus {
            outline: none;
            background: #ffffff;
            border-color: #128c7e;
            box-shadow: 0 4px 16px rgba(18, 140, 126, 0.15), 0 2px 8px rgba(16, 24, 40, 0.08);
            transform: translateY(-1px);
        }
        
        .search-bar::before {
            content: '🔍';
            position: absolute;
            left: 32px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1rem;
            opacity: 0.7;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        
        .search-input:focus + .search-bar::before {
            opacity: 1;
        }
        
        .conversations-list {
            flex: 1;
            overflow-y: auto;
            background: white;
        }
        
        .conversation-item {
            display: flex;
            align-items: center;
            padding: 16px 20px;
            cursor: pointer;
            border-bottom: 1px solid #f0f2f5;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            background: #ffffff;
        }
        
        .conversation-item:hover {
            background: linear-gradient(135deg, #f8fffe 0%, #f0f9f7 100%);
            transform: translateX(2px);
            box-shadow: 0 2px 12px rgba(18, 140, 126, 0.08);
        }
        
        .conversation-item.active {
            background: #e7f3ff;
            border-right: 3px solid #00a884;
        }
        
        .conversation-avatar {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1.2rem;
            flex-shrink: 0;
            margin-right: 16px;
        }
        
        .conversation-content {
            flex: 1;
            min-width: 0;
        }
        
        .conversation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2px;
        }
        
        .conversation-name {
            font-size: 0.95rem;
            font-weight: 600;
            color: #111b21;
            margin: 0;
            truncate-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
        }
        
        .conversation-time {
            font-size: 0.8rem;
            color: #667781;
            flex-shrink: 0;
            margin-left: 8px;
        }
        
        .conversation-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .conversation-message {
            font-size: 0.85rem;
            color: #667781;
            margin: 0;
            truncate-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
            flex: 1;
        }
        
        .unread-badge {
            background: #00a884;
            color: white;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 12px;
            min-width: 18px;
            text-align: center;
            margin-left: 8px;
        }
        
        /* Chat Panel - Ultra Elegant WhatsApp Design */
        .chat-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: linear-gradient(135deg, #f0f4f1 0%, #e8f0ed 100%);
            position: relative;
            overflow: hidden;
        }
        
        .chat-panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 50%, rgba(18, 140, 126, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(18, 140, 126, 0.02) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(18, 140, 126, 0.02) 0%, transparent 50%),
                linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 100%);
            pointer-events: none;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #ffffff 0%, #f8fffe 100%);
            padding: 20px 24px;
            border-bottom: 1px solid #e3f2f0;
            display: none;
            position: relative;
            z-index: 1;
            box-shadow: 0 2px 12px rgba(18, 140, 126, 0.08);
        }
        
        .chat-header.active {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .chat-contact-avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        
        .chat-contact-info h4 {
            margin: 0 0 2px 0;
            font-size: 1.1rem;
            font-weight: 600;
            color: #111b21;
        }
        
        .chat-contact-info p {
            margin: 0;
            color: #667781;
            font-size: 0.85rem;
        }
        
        .messages-container {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            position: relative;
            z-index: 1;
        }
        
        .empty-chat-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #667781;
            text-align: center;
        }
        
        .empty-chat-icon {
            font-size: 4rem;
            margin-bottom: 16px;
            opacity: 0.7;
        }
        
        .empty-chat-state h3 {
            font-size: 1.4rem;
            font-weight: 400;
            color: #41525d;
            margin: 0 0 8px 0;
        }
        
        .empty-chat-state p {
            font-size: 0.9rem;
            color: #667781;
            margin: 0;
        }
        
        /* Message Input Area - Professional Design */
        .message-input-area {
            background: linear-gradient(135deg, #ffffff 0%, #f8fffe 100%);
            padding: 20px 24px;
            display: none;
            position: relative;
            z-index: 1;
            border-top: 1px solid #e3f2f0;
            box-shadow: 0 -2px 12px rgba(18, 140, 126, 0.08);
        }
        
        .message-input-area.active {
            display: flex;
            gap: 16px;
            align-items: flex-end;
        }
        
        .message-input {
            flex: 1;
            min-height: 48px;
            max-height: 120px;
            padding: 14px 20px;
            border: 2px solid transparent;
            border-radius: 28px;
            background: #ffffff;
            font-family: inherit;
            font-size: 0.95rem;
            line-height: 1.5;
            resize: none;
            outline: none;
            box-shadow: 0 2px 12px rgba(16, 24, 40, 0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 400;
        }
        
        .message-input:focus {
            border-color: #128c7e;
            box-shadow: 0 4px 20px rgba(18, 140, 126, 0.15), 0 2px 12px rgba(16, 24, 40, 0.08);
            transform: translateY(-1px);
        }
        
        .message-input::placeholder {
            color: #6c737f;
            font-weight: 400;
        }
        
        .message-input-area .btn-success {
            min-width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(135deg, #128c7e 0%, #00a884 100%);
            border: none;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(18, 140, 126, 0.25);
        }
        
        .message-input-area .btn-success:hover {
            background: linear-gradient(135deg, #0f7269 0%, #008f6c 100%);
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 24px rgba(18, 140, 126, 0.35);
        }
        
        .message-input-area .btn-success:active {
            transform: translateY(-1px) scale(1.02);
            box-shadow: 0 4px 16px rgba(18, 140, 126, 0.25);
        }
        
        /* Header Clean Design */
        .header { 
            text-align: center; 
            margin-bottom: 1.5rem;
            padding: 1rem 0;
        }
        .header h1 { 
            font-size: 1.5rem; 
            font-weight: 700;
            margin-bottom: 0.25rem; 
            color: var(--text-primary);
        }
        .header p { 
            font-size: 0.9rem; 
            color: var(--text-secondary);
            font-weight: 400;
            margin: 0;
        }
        
        /* Navigation Clean */
        .nav { 
            display: flex; 
            gap: 0.5rem; 
            margin-bottom: 2rem; 
            flex-wrap: wrap; 
            justify-content: center;
            background: white;
            padding: 1rem;
            border-radius: 0.75rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }
        .nav-btn { 
            background: white; 
            border: 1px solid var(--border);
            padding: 0.75rem 1.25rem; 
            border-radius: 0.5rem; 
            cursor: pointer; 
            font-weight: 500; 
            transition: all 0.2s ease;
            color: var(--text-secondary);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .nav-btn:hover { 
            background: var(--bg-primary); 
            color: var(--text-primary);
            border-color: var(--primary);
        }
        .nav-btn.active { 
            background: var(--primary); 
            color: white;
            border-color: var(--primary);
        }
        
        /* Cards com design avançado */
        .card { 
            background: white; 
            border-radius: 1rem; 
            padding: 1.5rem; 
            box-shadow: var(--shadow-lg);
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }
        
        /* ===================== INSTÂNCIAS - DESIGN PROFISSIONAL ===================== */
        .instances-section {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
        }
        
        .instances-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--bg-primary);
        }
        
        .instances-header h2 {
            color: var(--text-primary);
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .instances-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); 
            gap: 1.25rem; 
        }
        
        .instance-card { 
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 2px solid var(--border); 
            border-radius: 1rem; 
            padding: 1.5rem; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .instance-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--border);
            transition: all 0.3s ease;
        }
        
        .instance-card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 8px 25px rgba(11,20,26,.15);
            border-color: var(--primary);
        }
        
        .instance-card:hover::before {
            background: var(--primary);
        }
        
        .instance-card.connected { 
            border-color: var(--primary-light); 
            background: linear-gradient(135deg, rgba(37, 211, 102, 0.03) 0%, #ffffff 100%);
        }
        
        .instance-card.connected::before {
            background: var(--primary-light);
        }
        
        .instance-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .instance-info h3 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .instance-id {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-family: 'Monaco', monospace;
        }
        
        .instance-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin: 1rem 0;
        }
        
        .stat-box {
            text-align: center;
            padding: 0.75rem;
            background: var(--bg-primary);
            border-radius: 0.5rem;
            border: 1px solid var(--border);
        }
        
        .stat-number {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        .instance-actions {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            justify-content: flex-start;
            flex-wrap: wrap;
        }
        
        .instance-actions .btn {
            flex: 0 0 auto;
            min-width: auto;
            padding: 0.5rem 0.75rem;
            font-size: 0.8rem;
        }
        
        .instance-actions .btn-sm {
            padding: 0.4rem 0.6rem;
            font-size: 0.75rem;
        }
        
        /* ===================== MENSAGENS - DESIGN WHATSAPP WEB ===================== */
        .messages-section {
            background: white;
            border-radius: 1rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
            height: 600px;
            display: flex;
            flex-direction: column;
        }
        
        .messages-header {
            padding: 1rem 1.5rem;
            border-bottom: 2px solid var(--bg-primary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .messages-header h2 {
            color: var(--text-primary);
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .instance-selector {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .instance-selector select {
            padding: 0.5rem 0.75rem;
            border: 2px solid var(--border);
            border-radius: 0.5rem;
            background: white;
            color: var(--text-primary);
            font-weight: 500;
            min-width: 150px;
        }
        
        .messages-content {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .conversations-panel {
            width: 320px;
            border-right: 2px solid var(--bg-primary);
            display: flex;
            flex-direction: column;
        }
        
        .conversations-header {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        .search-box {
            width: 100%;
            padding: 14px 20px 14px 48px;
            border: 2px solid transparent;
            border-radius: 28px;
            font-size: 0.95rem;
            background: #ffffff;
            color: #1c2025;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 8px rgba(16, 24, 40, 0.08);
            font-weight: 400;
            letter-spacing: 0.01em;
            position: relative;
        }
        
        .search-box::placeholder {
            color: #6c737f;
            font-weight: 400;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #128c7e;
            box-shadow: 0 4px 16px rgba(18, 140, 126, 0.15), 0 2px 8px rgba(16, 24, 40, 0.08);
            transform: translateY(-1px);
        }
        
        .conversations-list {
            flex: 1;
            overflow-y: auto;
        }
        
        .conversation-item {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .conversation-item:hover {
            background: var(--bg-primary);
        }
        
        .conversation-item.active {
            background: var(--primary-light);
            color: white;
        }
        
        .conversation-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--gradient-primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        
        .conversation-info {
            flex: 1;
            min-width: 0;
        }
        
        .conversation-name {
            font-weight: 600;
            margin-bottom: 0.25rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .conversation-last-message {
            font-size: 0.85rem;
            opacity: 0.8;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .conversation-meta {
            text-align: right;
            flex-shrink: 0;
        }
        
        .conversation-time {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-bottom: 0.25rem;
        }
        
        .unread-badge {
            background: var(--primary-light);
            color: white;
            border-radius: 50%;
            padding: 0.15rem 0.4rem;
            font-size: 0.7rem;
            font-weight: 600;
            min-width: 18px;
            text-align: center;
        }
        
        .chat-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        /* Chat panel improvements */
        .chat-header {
            display: none;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            background: var(--bg-secondary);
        }
        
        .chat-header.active {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .chat-contact-avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .chat-contact-info h4 {
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .chat-contact-info p {
            margin: 0;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        /* Conversation avatars */
        .conversation-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        
        .messages-container {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            background: linear-gradient(to bottom, var(--bg-chat) 0%, #efeae2 100%);
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
                radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 2px, transparent 2px);
            background-size: 60px 60px;
        }
        
        .message-bubble {
            max-width: 70%;
            margin-bottom: 0.75rem;
            display: flex;
        }
        
        .message-bubble.outgoing {
            justify-content: flex-end;
        }
        
        .message-bubble.incoming {
            justify-content: flex-start;
        }
        
        .message-content {
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            position: relative;
            word-wrap: break-word;
        }
        
        .message-content.outgoing {
            background: var(--primary-light);
            color: white;
            border-bottom-right-radius: 0.25rem;
        }
        
        .message-content.incoming {
            background: white;
            color: var(--text-primary);
            border-bottom-left-radius: 0.25rem;
            box-shadow: var(--shadow);
        }
        
        .message-text {
            line-height: 1.4;
            margin-bottom: 0.25rem;
        }
        
        .message-time {
            font-size: 0.7rem;
            opacity: 0.8;
            text-align: right;
        }
        
        /* Message input improvements */
        .message-input-area {
            display: none;
            padding: 1rem 1.5rem;
            border-top: 1px solid var(--border);
            background: white;
            gap: 12px;
            align-items: flex-end;
        }
        
        .message-input-area.active {
            display: flex;
        }
        
        .message-input {
            flex: 1;
            min-height: 42px;
            max-height: 120px;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 24px;
            resize: none;
            font-family: inherit;
            font-size: 0.95rem;
            line-height: 1.4;
            transition: all 0.3s ease;
            outline: none;
        }
        
        .message-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 211, 102, 0.1);
        }
        
        .message-input::placeholder {
            color: #8e9297;
        }
        
        /* Send button improvements */
        .message-input-area .btn-success {
            min-width: 90px;
            height: 42px;
            border-radius: 21px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .message-input-area .btn-success:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
        }
        
        .message-input:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .empty-chat-state {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            color: var(--text-secondary);
            text-align: center;
        }
        
        /* Groups Section Styles */
        .groups-container {
            margin-top: 1rem;
        }
        
        .groups-header {
            margin-bottom: 1rem;
        }
        
        .group-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 0.5rem;
            background: var(--bg-secondary);
            transition: all 0.3s ease;
        }
        
        .group-card:hover {
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .group-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .group-avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .group-details h4 {
            margin: 0 0 0.25rem 0;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .group-details p {
            margin: 0 0 0.25rem 0;
            color: var(--text-muted);
            font-size: 0.85rem;
        }
        
        .group-details small {
            color: var(--text-muted);
            font-size: 0.75rem;
        }
        
        .group-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .schedule-panel {
            border-top: 1px solid var(--border);
            padding-top: 1.5rem;
        }

        .preview-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1rem;
        }

        .scheduled-messages {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-top: 1rem;
        }

        .scheduled-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-secondary);
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: var(--shadow);
        }

        .scheduled-info {
            display: flex;
            flex-direction: column;
        }

        .scheduled-info span {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .empty-chat-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        /* Status Indicators Profissionais */
        .status-indicator { 
            display: inline-flex; 
            align-items: center; 
            gap: 0.4rem; 
            padding: 0.4rem 0.8rem; 
            border-radius: 1.5rem; 
            font-weight: 500;
            font-size: 0.8rem;
        }
        .status-connected { 
            background: rgba(37, 211, 102, 0.1); 
            color: var(--primary-light);
            border: 1px solid rgba(37, 211, 102, 0.2);
        }
        .status-disconnected { 
            background: rgba(239, 68, 68, 0.1); 
            color: #dc2626;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        .status-connecting { 
            background: rgba(245, 158, 11, 0.1); 
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        .status-dot { 
            width: 6px; 
            height: 6px; 
            border-radius: 50%; 
        }
        .status-connected .status-dot { background: var(--primary-light); }
        .status-disconnected .status-dot { background: #dc2626; }
        .status-connecting .status-dot { 
            background: #f59e0b; 
            animation: pulse 2s infinite; 
        }
        
        /* Buttons Clean */
        .btn { 
            padding: 0.5rem 1rem; 
            border: 1px solid var(--border); 
            border-radius: 0.5rem; 
            cursor: pointer; 
            font-weight: 500; 
            font-size: 0.875rem;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            justify-content: center;
            line-height: 1.2;
        }
        .btn-primary { 
            background: var(--primary); 
            color: white;
            border-color: var(--primary);
        }
        .btn-primary:hover {
            background: var(--primary-dark);
            border-color: var(--primary-dark);
        }
        .btn-success { 
            background: var(--primary-light); 
            color: white;
            border-color: var(--primary-light);
        }
        .btn-success:hover {
            background: var(--primary);
            border-color: var(--primary);
        }
        .btn-danger { 
            background: #dc2626; 
            color: white;
            border-color: #dc2626;
        }
        .btn-danger:hover {
            background: #b91c1c;
            border-color: #b91c1c;
        }
        .btn-secondary {
            background: white;
            color: var(--text-secondary);
            border-color: var(--border);
        }
        .btn-secondary:hover {
            background: var(--bg-primary);
            color: var(--text-primary);
        }
        .btn:disabled { 
            opacity: 0.5; 
            cursor: not-allowed; 
        }
        .btn-sm {
            padding: 0.4rem 0.75rem;
            font-size: 0.8rem;
        }
        
        /* WebSocket Status Clean */
        .websocket-status {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 0.5rem 0.75rem;
            border-radius: 0.5rem;
            font-size: 0.8rem;
            font-weight: 500;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .websocket-connected {
            background: rgba(37, 211, 102, 0.1);
            color: var(--primary-light);
            border: 1px solid rgba(37, 211, 102, 0.2);
        }
        .websocket-disconnected {
            background: rgba(239, 68, 68, 0.1);
            color: #dc2626;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        
        /* Stats Grid Moderno */
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; 
            margin: 1.5rem 0; 
        }
        .stat-card { 
            text-align: center; 
            padding: 1.5rem; 
            background: linear-gradient(135deg, var(--bg-primary) 0%, white 100%);
            border-radius: 1rem; 
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        .stat-number { 
            font-size: 2rem; 
            font-weight: 800; 
            color: var(--primary); 
            margin-bottom: 0.5rem; 
        }
        .stat-label { 
            color: var(--text-secondary); 
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        /* Empty State Profissional */
        .empty-state { 
            text-align: center; 
            padding: 3rem 1.5rem; 
            color: var(--text-secondary); 
        }
        .empty-icon { 
            font-size: 3rem; 
            margin-bottom: 1rem; 
            opacity: 0.5; 
        }
        .empty-title { 
            font-size: 1.25rem; 
            font-weight: 600; 
            color: var(--text-primary); 
            margin-bottom: 0.5rem; 
        }
        
        /* Section Management */
        .section { display: none; }
        .section.active { display: block; }
        
        /* Modal */
        .modal { 
            display: none; 
            position: fixed; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: rgba(17, 24, 39, 0.8); 
            backdrop-filter: blur(8px);
            z-index: 1000; 
            align-items: center; 
            justify-content: center; 
        }
        .modal.show { display: flex; }
        .modal-content { 
            background: white; 
            padding: 2rem; 
            border-radius: 1.5rem; 
            width: 90%; 
            max-width: 500px; 
            position: relative; 
            z-index: 1002;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border);
        }
        
        /* Forms */
        .form-input { 
            width: 100%; 
            padding: 0.875rem; 
            border: 2px solid var(--border); 
            border-radius: 0.6rem; 
            font-size: 0.9rem;
            transition: all 0.3s ease;
            background: white;
        }
        .form-input:focus { 
            outline: none; 
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(18, 140, 126, 0.1);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .header h1 { font-size: 2rem; }
            .nav { padding: 0.5rem; flex-direction: column; }
            .instances-grid { grid-template-columns: 1fr; }
            .messages-content { flex-direction: column; }
            .conversations-panel { width: 100%; }
            .instance-actions { grid-template-columns: 1fr; }
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .chat-item:hover {
            background: var(--bg-primary);
            transform: translateX(4px);
        }
        .chat-item:last-child {
            border-bottom: none;
        }
        
        .contact-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            flex-shrink: 0;
            box-shadow: var(--shadow);
        }
        .contact-avatar img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .chat-info {
            flex: 1;
            min-width: 0;
        }
        .chat-name {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        .chat-message {
            color: var(--text-secondary);
            font-size: 0.9rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .chat-time {
            color: var(--text-secondary);
            font-size: 0.8rem;
            flex-shrink: 0;
        }
        
        /* Status Indicators */
        .status-indicator { 
            display: inline-flex; 
            align-items: center; 
            gap: 0.5rem; 
            padding: 0.5rem 1rem; 
            border-radius: 2rem; 
            font-weight: 500;
            font-size: 0.9rem;
        }
        .status-connected { 
            background: rgba(37, 211, 102, 0.1); 
            color: var(--primary-light);
            border: 1px solid rgba(37, 211, 102, 0.2);
        }
        .status-disconnected { 
            background: rgba(239, 68, 68, 0.1); 
            color: #dc2626;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        .status-connecting { 
            background: rgba(245, 158, 11, 0.1); 
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        .status-dot { 
            width: 8px; 
            height: 8px; 
            border-radius: 50%; 
        }
        .status-connected .status-dot { background: var(--primary-light); }
        .status-disconnected .status-dot { background: #dc2626; }
        .status-connecting .status-dot { 
            background: #f59e0b; 
            animation: pulse 2s infinite; 
        }
        
        /* Stats Grid */
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
            margin: 2rem 0; 
        }
        .stat-card { 
            text-align: center; 
            padding: 2rem; 
            background: linear-gradient(135deg, var(--bg-primary) 0%, white 100%);
            border-radius: 1rem; 
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        .stat-number { 
            font-size: 2.5rem; 
            font-weight: 800; 
            color: var(--primary); 
            margin-bottom: 0.5rem; 
        }
        .stat-label { 
            color: var(--text-secondary); 
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        /* Instance Cards */
        .instances-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 1.5rem; 
        }
        .instance-card { 
            border: 2px solid var(--border); 
            border-radius: 1rem; 
            padding: 1.5rem; 
            background: white; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .instance-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--border);
            transition: all 0.3s ease;
        }
        .instance-card:hover { 
            transform: translateY(-4px); 
            box-shadow: var(--shadow-lg);
            border-color: var(--primary);
        }
        .instance-card:hover::before {
            background: var(--primary);
        }
        .instance-card.connected { 
            border-color: var(--primary-light); 
            background: linear-gradient(135deg, rgba(37, 211, 102, 0.02) 0%, white 100%);
        }
        .instance-card.connected::before {
            background: var(--primary-light);
        }
        
        /* Buttons */
        .btn { 
            padding: 0.75rem 1.5rem; 
            border: none; 
            border-radius: 0.75rem; 
            cursor: pointer; 
            font-weight: 600; 
            font-size: 0.9rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn-primary { 
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); 
            color: white;
            box-shadow: var(--shadow);
        }
        .btn-success { 
            background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%); 
            color: white;
            box-shadow: var(--shadow);
        }
        .btn-danger { 
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); 
            color: white;
            box-shadow: var(--shadow);
        }
        .btn-secondary {
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: var(--shadow-lg);
        }
        .btn:disabled { 
            opacity: 0.5; 
            cursor: not-allowed; 
            transform: none;
        }
        
        /* Modal */
        .modal { 
            display: none; 
            position: fixed; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: rgba(17, 24, 39, 0.75); 
            backdrop-filter: blur(4px);
            z-index: 1000; 
            align-items: center; 
            justify-content: center; 
        }
        .modal.show { display: flex; }
        .modal-content { 
            background: white; 
            padding: 2rem; 
            border-radius: 1.5rem; 
            width: 90%; 
            max-width: 500px; 
            position: relative; 
            z-index: 1002;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
        }
        .modal-content * { position: relative; z-index: 1003; }
        .modal-content input, .modal-content button { pointer-events: all; }
        .modal { pointer-events: all; }
        .modal-content { pointer-events: all; }
        
        /* Forms */
        .form-input { 
            width: 100%; 
            padding: 1rem; 
            border: 2px solid var(--border); 
            border-radius: 0.75rem; 
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .form-input:focus { 
            outline: none; 
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(18, 140, 126, 0.1);
        }
        
        /* Empty State */
        .empty-state { 
            text-align: center; 
            padding: 4rem 2rem; 
            color: var(--text-secondary); 
        }
        .empty-icon { 
            font-size: 4rem; 
            margin-bottom: 1.5rem; 
            opacity: 0.5; 
        }
        .empty-title { 
            font-size: 1.5rem; 
            font-weight: 600; 
            color: var(--text-primary); 
            margin-bottom: 0.5rem; 
        }
        
        /* Section Management */
        .section { display: none; }
        .section.active { display: block; }
        
        /* Messages */
        .success-message { 
            background: rgba(37, 211, 102, 0.1); 
            color: var(--primary-light); 
            padding: 1rem; 
            border-radius: 0.75rem; 
            margin: 1.5rem 0; 
            text-align: center; 
            font-weight: 500;
            border: 1px solid rgba(37, 211, 102, 0.2);
        }
        
        /* QR Code Container */
        .qr-container { 
            text-align: center; 
            margin: 2rem 0; 
        }
        .qr-code { 
            background: white; 
            padding: 2rem; 
            border-radius: 1rem; 
            box-shadow: var(--shadow-lg);
            display: inline-block;
            border: 1px solid var(--border);
        }
        
        /* Additional styles for existing elements */
        .real-connection-badge { 
            background: var(--primary-light); 
            color: white; 
            padding: 1rem 1.5rem; 
            border-radius: 0.75rem; 
            margin: 1.5rem 0; 
            text-align: center; 
            font-weight: 600;
            box-shadow: var(--shadow);
        }
        
        .qr-instructions { 
            background: var(--bg-primary); 
            padding: 1.5rem; 
            border-radius: 0.75rem; 
            margin-bottom: 1.5rem; 
            text-align: left;
            border: 1px solid var(--border);
        }
        
        .connected-user { 
            background: rgba(37, 211, 102, 0.1); 
            padding: 1rem; 
            border-radius: 0.75rem; 
            margin: 1rem 0; 
            border: 2px solid var(--primary-light);
        }
        
        .loading { 
            text-align: center; 
            padding: 2.5rem; 
            color: var(--text-secondary); 
        }
        .loading-spinner { 
            font-size: 2rem; 
            margin-bottom: 1rem; 
            animation: pulse 1s infinite; 
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .header h1 { font-size: 2rem; }
            .nav { padding: 0.5rem; }
            .stats-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
            .instances-grid { grid-template-columns: 1fr; }
            .modal-content { margin: 1rem; width: calc(100% - 2rem); }
        }
        
        /* Loading States */
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: var(--text-secondary);
        }
        
        .loading-spinner {
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="websocket-status" id="websocketStatus">🔄 Conectando</div>
    
    <div class="container">
        <nav class="nav">
            <button class="nav-btn active" onclick="showSection('dashboard')">
                <span>📊</span> Dashboard
            </button>
            <button class="nav-btn" onclick="showSection('instances')">
                <span>📱</span> Instâncias
            </button>
            <button class="nav-btn" onclick="showSection('contacts')">
                <span>👥</span> Contatos
            </button>
            <button class="nav-btn" onclick="showSection('messages')">
                <span>💬</span> Mensagens
            </button>
            <button class="nav-btn" onclick="showSection('groups')">
                <span>👥</span> Grupos
            </button>
            <button class="nav-btn" onclick="showSection('flows')">
                <span>🎯</span> Fluxos
            </button>
            <button class="nav-btn" onclick="showSection('campaigns')">
                <span>📢</span> Campanhas
            </button>
        </nav>
        
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>Status da Conexão</h2>
                <div id="connection-status" class="status-indicator status-disconnected">
                    <div class="status-dot"></div>
                    <span>Verificando conexão...</span>
                </div>
                <div id="connected-user-info" style="display: none;"></div>
            </div>
            
            <div class="card">
                <h2>Estatísticas</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="contacts-count">0</div>
                        <div class="stat-label">Contatos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="conversations-count">0</div>
                        <div class="stat-label">Conversas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="messages-count">0</div>
                        <div class="stat-label">Mensagens</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="instances-count">0</div>
                        <div class="stat-label">Instâncias</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Instances Section - Design Profissional -->
        <div id="instances" class="section">
            <div class="instances-section">
                <div class="instances-header">
                    <h2>Gerenciar Instâncias</h2>
                    <button class="btn btn-primary" onclick="showCreateModal()">
                        Nova Instância
                    </button>
                </div>
                <div id="instances-container" class="instances-grid">
                    <div class="loading" style="grid-column: 1 / -1;">
                        <div style="text-align: center; padding: 2rem;">Carregando instâncias...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Messages Section - Design WhatsApp Web Fullscreen -->
        <div id="messages" class="section">
            <div class="messages-section">
                <div class="messages-header">
                    <h2>Central de Mensagens</h2>
                    <div class="instance-selector">
                        <label for="instanceSelect">Instância:</label>
                        <select id="instanceSelect" onchange="switchInstance()">
                            <option value="">Selecione uma instância</option>
                        </select>
                        <button class="btn btn-secondary" onclick="loadConversations()">🔄 Atualizar</button>
                    </div>
                </div>
                
                <div class="messages-content">
                    <div class="conversations-panel">
                        <div class="search-bar">
                            <input type="text" placeholder="🔍 Buscar conversas..." class="search-input">
                        </div>
                        <div class="conversations-list" id="conversationsList">
                            <div class="empty-state">
                                <div class="empty-icon">💬</div>
                                <div class="empty-title">Nenhuma conversa</div>
                                <p>Selecione uma instância para ver as conversas</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chat-panel">
                        <div class="chat-header" id="chatHeader">
                            <div class="chat-contact-avatar" id="chatAvatar">?</div>
                            <div class="chat-contact-info">
                                <h4 id="chatContactName">Nome do Contato</h4>
                                <p id="chatContactPhone">+55 11 99999-9999</p>
                            </div>
                        </div>
                        
                        <div class="messages-container" id="messagesContainer">
                            <div class="empty-chat-state">
                                <div class="empty-chat-icon">💭</div>
                                <h3>Selecione uma conversa</h3>
                                <p>Escolha uma conversa da lista para visualizar mensagens</p>
                            </div>
                        </div>
                        
                        <div class="message-input-area" id="messageInputArea">
                            <textarea class="message-input" id="messageInput" 
                                      placeholder="Digite sua mensagem..." 
                                      onkeypress="handleMessageKeyPress(event)"></textarea>
                            <button class="btn btn-success" onclick="sendMessage()">
                                📤 Enviar
                            </button>
                            <button class="btn btn-secondary" onclick="sendWebhook()" title="Enviar Webhook">
                                🔗 Webhook
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Contacts Section -->
        <div id="contacts" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2>👥 Central de Contatos</h2>
                    <button class="btn btn-primary" onclick="loadContacts()">🔄 Atualizar</button>
                </div>
                <div id="contacts-container">
                    <div class="loading">
                        <div style="text-align: center; padding: 2rem;">Carregando contatos...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Schedule Section -->
        <div id="groups" class="section">
            <div class="card">
                <div class="schedule-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2>📅 Agendamentos de Mensagens</h2>
                    <button class="btn btn-primary" onclick="openScheduleModal()">+ Agendar mensagem</button>
                </div>
                <div class="preview-controls">
                    <label for="previewWeekday">Dia da semana:</label>
                    <select id="previewWeekday" onchange="loadScheduledMessages()">
                        <option value="0">Domingo</option>
                        <option value="1">Segunda</option>
                        <option value="2">Terça</option>
                        <option value="3">Quarta</option>
                        <option value="4">Quinta</option>
                        <option value="5">Sexta</option>
                        <option value="6">Sábado</option>
                    </select>
                </div>
                <div class="scheduled-messages" id="scheduledMessages">
                    <div class="empty-state">
                        <p>Nenhuma mensagem agendada</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Schedule Modal -->
        <div id="scheduleModal" class="modal" style="display:none;">
            <div class="modal-content">
                <span class="close" onclick="closeScheduleModal()">&times;</span>
                <h3>Agendar Mensagem</h3>
                <div class="form-group">
                    <label>Instância</label>
                    <select id="scheduleInstanceSelect" onchange="loadGroupsForSchedule()">
                        <option value="">Selecione uma instância</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Grupo</label>
                    <select id="scheduleGroupSelect">
                        <option value="">Selecione um grupo</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Dia da semana</label>
                    <select id="weekdaySelect">
                        <option value="0">Domingo</option>
                        <option value="1">Segunda</option>
                        <option value="2">Terça</option>
                        <option value="3">Quarta</option>
                        <option value="4">Quinta</option>
                        <option value="5">Sexta</option>
                        <option value="6">Sábado</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Horário</label>
                    <input type="time" id="scheduleTime">
                </div>
                <div class="form-group">
                    <label>Tipo de mensagem</label>
                    <select id="messageType" onchange="toggleMediaInput()">
                        <option value="text">Texto</option>
                        <option value="image">Imagem</option>
                        <option value="audio">Áudio</option>
                        <option value="video">Vídeo</option>
                    </select>
                </div>
                <div class="form-group">
                    <textarea id="scheduleText" placeholder="Mensagem..." style="width:100%;height:80px;"></textarea>
                    <input type="file" id="scheduleMedia" style="display:none;margin-top:10px;" accept="image/*,audio/*,video/*">
                </div>
                <button class="btn btn-success" onclick="submitSchedule()">📤 Agendar</button>
            </div>
        </div>
        
        <!-- Flows Section - Funcionalidade existente -->
        <div id="flows" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2>🎯 Fluxos de Automação</h2>
                    <button class="btn btn-primary" onclick="createNewFlow()">
                        ➕ Criar Novo Fluxo
                    </button>
                </div>
                <div id="flows-container">
                    <div class="empty-state">
                        <div class="empty-icon">🎯</div>
                        <div class="empty-title">Nenhum fluxo criado ainda</div>
                        <p>Crie fluxos de automação drag-and-drop para otimizar seu atendimento</p>
                        <br>
                        <button class="btn btn-primary" onclick="createNewFlow()">
                            🚀 Criar Primeiro Fluxo
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div id="campaigns" class="section">
            <div class="card">
                <h2>📢 Campanhas</h2>
                <form id="campaignForm" onsubmit="createCampaign(event)">
                    <input type="text" id="campName" placeholder="Nome" class="form-input" required>
                    <input type="text" id="campDesc" placeholder="Descrição" class="form-input" style="margin-top:10px">
                    <div style="display:flex; gap:10px; margin-top:10px">
                        <select id="campRecurrence" class="form-input">
                            <option value="once">Uma vez</option>
                            <option value="daily">Diária</option>
                            <option value="weekly">Semanal</option>
                        </select>
                        <input type="time" id="campTime" class="form-input" required>
                        <select id="campWeekday" class="form-input">
                            <option value="">-</option>
                            <option value="0">Dom</option>
                            <option value="1">Seg</option>
                            <option value="2">Ter</option>
                            <option value="3">Qua</option>
                            <option value="4">Qui</option>
                            <option value="5">Sex</option>
                            <option value="6">Sáb</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" style="margin-top:10px" type="submit">Criar campanha</button>
                </form>
                <div id="campaignList" style="margin-top:1rem"></div>
            </div>
            <div class="card" style="margin-top:1rem">
                <h3>Agendar mensagem</h3>
                <form id="scheduleForm" onsubmit="scheduleMessage(event)">
                    <select id="scheduleCampaign" class="form-input" required></select>
                    <select id="scheduleGroups" class="form-input" multiple style="margin-top:10px"></select>
                    <textarea id="scheduleContent" class="form-input" placeholder="Mensagem" style="margin-top:10px"></textarea>
                    <div style="display:flex; gap:10px; margin-top:10px">
                        <select id="scheduleMediaType" class="form-input">
                            <option value="text">Texto</option>
                            <option value="image">Imagem</option>
                            <option value="audio">Áudio</option>
                            <option value="video">Vídeo</option>
                        </select>
                        <input type="text" id="scheduleMediaPath" class="form-input" placeholder="Caminho mídia">
                    </div>
                    <button class="btn btn-primary" style="margin-top:10px" type="submit">Agendar</button>
                </form>
                <div id="scheduledList" style="margin-top:1rem"></div>
            </div>
        </div>
    </div>

    <div id="createModal" class="modal">
        <div class="modal-content">
            <h3>➕ Nova Instância WhatsApp</h3>
            <form onsubmit="createInstance(event)">
                <div style="margin: 20px 0;">
                    <input type="text" id="instanceName" class="form-input" 
                           placeholder="Nome da instância" required>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn" onclick="hideCreateModal()">Cancelar</button>
                    <button type="submit" class="btn btn-success" style="flex: 1;">Criar</button>
                </div>
            </form>
        </div>
    </div>
    
    <div id="qrModal" class="modal">
        <div class="modal-content">
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <h3>📱 Conectar WhatsApp Real - <span id="qr-instance-name">Instância</span></h3>
                <button onclick="closeQRModal()" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
            </div>
            
            <div id="connection-status" style="text-align: center; margin-bottom: 15px; font-weight: bold;">
                ⏳ Preparando conexão...
            </div>
            
            <div class="qr-instructions">
                <h4>📲 Como conectar seu WhatsApp:</h4>
                <ol>
                    <li>Abra o <strong>WhatsApp</strong> no seu celular</li>
                    <li>Toque em <strong>Configurações ⚙️</strong></li>
                    <li>Toque em <strong>Aparelhos conectados</strong></li>
                    <li>Toque em <strong>Conectar um aparelho</strong></li>
                    <li><strong>Escaneie o QR Code</strong> abaixo</li>
                </ol>
            </div>
            
            <div id="qr-code-container" class="qr-container">
                <div id="qr-loading" style="text-align: center; padding: 40px;">
                    <div style="font-size: 2rem; margin-bottom: 15px;">⏳</div>
                    <p>Gerando QR Code real...</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-danger" onclick="closeQRModal()">🚫 Fechar</button>
            </div>
        </div>
    </div>

    <script>
        let instances = [];
        let currentInstanceId = null;
        let qrPollingInterval = null;
        let statusPollingInterval = null;

        function showSection(name) {
            console.log('📄 Tentando mostrar seção:', name);
            
            // Hide all sections
            const sections = document.querySelectorAll('.section');
            sections.forEach(s => {
                s.classList.remove('active');
                s.style.display = 'none';
            });
            
            // Remove active class from all nav buttons
            const navButtons = document.querySelectorAll('.nav-btn');
            navButtons.forEach(b => b.classList.remove('active'));
            
            // Show selected section
            const targetSection = document.getElementById(name);
            if (targetSection) {
                targetSection.classList.add('active');
                targetSection.style.display = 'block';
                console.log('✅ Seção', name, 'ativada');
            } else {
                console.error('❌ Seção não encontrada:', name);
                return;
            }
            
            // Find and activate the correct button by checking onclick attribute
            navButtons.forEach(button => {
                const onclickAttr = button.getAttribute('onclick');
                if (onclickAttr && onclickAttr.includes(`'${name}'`)) {
                    button.classList.add('active');
                    console.log('✅ Botão ativo:', name);
                }
            });
            
            console.log('📄 Seção ativa:', name);
            
            // Load section-specific data
            if (name === 'dashboard') {
                loadStats();
                checkConnectionStatus();
            } else if (name === 'instances') {
                loadInstances();
            } else if (name === 'contacts') {
                loadContacts();
            } else if (name === 'messages') {
                // Only load if not already loaded to avoid double loading
                if (!document.getElementById('instanceSelect').innerHTML.includes('option')) {
                    loadInstancesForSelect();
                }
            } else if (name === 'groups') {
                loadScheduledMessages();
            } else if (name === 'flows') {
                loadFlows();
            }
        }

        function showCreateModal() {
            document.getElementById('createModal').classList.add('show');
        }

        function hideCreateModal() {
            document.getElementById('createModal').classList.remove('show');
            document.getElementById('instanceName').value = '';
        }

        let qrInterval = null;
        let currentQRInstance = null;

        async function showQRModal(instanceId) {
            console.log('🔄 Showing QR modal for instance:', instanceId);
            currentQRInstance = instanceId;
            
            // Check if elements exist before setting text
            const instanceNameEl = document.getElementById('qr-instance-name');
            if (instanceNameEl) {
                instanceNameEl.textContent = instanceId;
                console.log('✅ Instance name set');
            } else {
                console.error('❌ qr-instance-name element not found');
            }
            
            const modalEl = document.getElementById('qrModal');
            if (modalEl) {
                modalEl.classList.add('show');
                console.log('✅ Modal shown');
            } else {
                console.error('❌ qrModal element not found');
            }
            
            // Start QR polling
            loadQRCode();
            qrInterval = setInterval(loadQRCode, 3000); // Check every 3 seconds
        }

        async function loadQRCode() {
            if (!currentQRInstance) return;
            
            try {
                const [statusResponse, qrResponse] = await Promise.all([
                    fetch(`/api/whatsapp/status/${currentQRInstance}`),
                    fetch(`/api/whatsapp/qr/${currentQRInstance}`)
                ]);
                
                const status = await statusResponse.json();
                const qrData = await qrResponse.json();
                
                const qrContainer = document.getElementById('qr-code-container');
                const statusElement = document.getElementById('connection-status');
                
                if (status.connected && status.user) {
                    // Connected - show success
                    qrContainer.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <div style="font-size: 4em; margin-bottom: 20px;">✅</div>
                            <h3 style="color: #28a745; margin-bottom: 10px;">WhatsApp Conectado!</h3>
                            <p style="color: #666; margin-bottom: 10px;">Usuário: <strong>${status.user.name}</strong></p>
                            <p style="color: #666; margin-bottom: 20px;">Telefone: <strong>${status.user.phone || status.user.id.split(':')[0]}</strong></p>
                            <div style="margin-bottom: 20px;">
                                <button class="btn btn-success" onclick="closeQRModal()">🎉 Continuar</button>
                            </div>
                            <p style="font-size: 0.9em; color: #999;">Suas conversas serão importadas automaticamente</p>
                        </div>
                    `;
                    statusElement.textContent = '✅ Conectado e sincronizando conversas...';
                    statusElement.style.color = '#28a745';
                    
                    // Stop polling and reload conversations after 5 seconds
                    if (qrInterval) {
                        clearInterval(qrInterval);
                        qrInterval = null;
                    }
                    
                    // Auto-close modal and refresh data after showing success
                    setTimeout(() => {
                        closeQRModal();
                        // Refresh instance list and load conversations
                        if (document.getElementById('instances').style.display !== 'none') {
                            loadInstances();
                        }
                        // Load messages if on messages tab
                        if (document.getElementById('messages').style.display !== 'none') {
                            loadMessages();
                        }
                        // Load contacts if on contacts tab
                        if (document.getElementById('contacts').style.display !== 'none') {
                            loadContacts();
                        }
                    }, 3000);
                    
                } else if (status.connecting && qrData.qr) {
                    // Show QR code with expiration timer
                    const expiresIn = qrData.expiresIn || 60;
                    qrContainer.innerHTML = `
                        <div style="text-align: center;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&data=${encodeURIComponent(qrData.qr)}" 
                                 alt="QR Code" style="max-width: 280px; max-height: 280px; border: 2px solid #28a745; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                            <p style="margin-top: 15px; color: #666; font-weight: bold;">Escaneie o QR Code com seu WhatsApp</p>
                            <p style="font-size: 0.9em; color: #999; margin-bottom: 15px;">QR Code válido por ${expiresIn} segundos</p>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                <p style="margin: 0; font-size: 0.9em; color: #666;">
                                    💡 <strong>Dica:</strong> Abra WhatsApp → Configurações → Aparelhos conectados → Conectar aparelho
                                </p>
                            </div>
                        </div>
                    `;
                    statusElement.textContent = '📱 Aguardando escaneamento do QR Code...';
                    statusElement.style.color = '#007bff';
                    
                } else if (status.connecting) {
                    // Connecting but no QR yet
                    qrContainer.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <div class="loading-spinner" style="font-size: 3em; margin-bottom: 20px;">🔄</div>
                            <p style="color: #666;">Preparando conexão WhatsApp...</p>
                            <p style="font-size: 0.9em; color: #999;">QR Code será gerado em instantes</p>
                        </div>
                    `;
                    statusElement.textContent = '⏳ Preparando conexão...';
                    statusElement.style.color = '#ffc107';
                    
                } else {
                    // Not connected, not connecting
                    qrContainer.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <div style="font-size: 3em; margin-bottom: 20px;">📱</div>
                            <p style="color: #666; margin-bottom: 20px;">Instância não conectada</p>
                            <button class="btn btn-primary" onclick="connectInstance('${currentQRInstance}')">
                                🔗 Iniciar Conexão
                            </button>
                            <p style="font-size: 0.9em; color: #999; margin-top: 15px;">Clique para gerar um novo QR Code</p>
                        </div>
                    `;
                    statusElement.textContent = '❌ Desconectado';
                    statusElement.style.color = '#dc3545';
                }
                
            } catch (error) {
                console.error('Erro ao carregar QR code:', error);
                document.getElementById('qr-code-container').innerHTML = `
                    <div style="text-align: center; padding: 40px; color: red;">
                        <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                        <p>Erro ao carregar status da conexão</p>
                        <button class="btn btn-primary" onclick="loadQRCode()" style="margin-top: 15px;">🔄 Tentar Novamente</button>
                    </div>
                `;
                document.getElementById('connection-status').textContent = '❌ Erro de comunicação';
                document.getElementById('connection-status').style.color = '#dc3545';
            }
        }

        function closeQRModal() {
            document.getElementById('qrModal').classList.remove('show');
            currentQRInstance = null;
            
            // Stop QR polling
            if (qrInterval) {
                clearInterval(qrInterval);
                qrInterval = null;
            }
            
            // Reload instances to update status
            if (document.getElementById('instances').style.display !== 'none') {
                loadInstances();
            }
        }

        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                instances = await response.json();
                renderInstances();
            } catch (error) {
                document.getElementById('instances-container').innerHTML = 
                    '<div class="empty-state"><div class="empty-icon">❌</div><div class="empty-title">Erro ao carregar</div></div>';
            }
        }

        async function createInstance(event) {
            event.preventDefault();
            const name = document.getElementById('instanceName').value;
            
            try {
                const response = await fetch('/api/instances', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                
                if (response.ok) {
                    hideCreateModal();
                    loadInstances();
                    // Show both alert and console log for debugging
                    console.log(`✅ Instância "${name}" criada com sucesso!`);
                    alert(`✅ Instância "${name}" criada!`);
                } else {
                    console.error('❌ Response not OK:', response.status);
                    alert('❌ Erro: Resposta inválida do servidor');
                }
            } catch (error) {
                console.error('❌ Erro ao criar instância:', error);
                alert('❌ Erro ao criar instância: ' + error.message);
            }
        }

        async function connectInstance(instanceId) {
            console.log('🔄 Connecting instance:', instanceId);
            try {
                const response = await fetch(`/api/instances/${instanceId}/connect`, {
                    method: 'POST'
                });
                
                console.log('Response status:', response.status);
                
                if (response.ok) {
                    console.log('✅ Connection started, opening QR modal');
                    showQRModal(instanceId);
                } else {
                    console.error('❌ Connection failed:', response.status);
                    alert('❌ Erro ao iniciar conexão');
                }
            } catch (error) {
                console.error('❌ Connection error:', error);
                alert('❌ Erro de conexão');
            }
        }

        async function deleteInstance(id, name) {
            if (!confirm(`Excluir "${name}"?`)) return;
            
            try {
                const response = await fetch(`/api/instances/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    loadInstances();
                    alert(`✅ "${name}" excluída!`);
                }
            } catch (error) {
                alert('❌ Erro ao excluir');
            }
        }

        async function showQRCode(instanceId) {
            showQRModal(instanceId);
        }

        async function disconnectInstance(instanceId) {
            if (!confirm('Desconectar esta instância?')) return;
            
            try {
                const response = await fetch(`/api/instances/${instanceId}/disconnect`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    loadInstances();
                    alert('✅ Instância desconectada!');
                } else {
                    alert('❌ Erro ao desconectar');
                }
            } catch (error) {
                alert('❌ Erro de conexão');
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('contacts-count').textContent = stats.contacts_count || 0;
                document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
                document.getElementById('messages-count').textContent = stats.messages_count || 0;
            } catch (error) {
                console.error('Error loading stats');
            }
        }

        async function loadMessages() {
            try {
                // Load chat list
                const chatsResponse = await fetch('/api/chats');
                const chats = await chatsResponse.json();
                
                const chatList = document.getElementById('chat-list');
                if (chats.length === 0) {
                    chatList.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">💬</div>
                            <div class="empty-title">Nenhuma conversa</div>
                            <p>As conversas aparecerão aqui quando receber mensagens</p>
                        </div>
                    `;
                } else {
                    chatList.innerHTML = chats.map(chat => `
                        <div class="chat-item" onclick="openChat('${chat.contact_phone}', '${chat.contact_name}', '${chat.instance_id}')"
                             style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; hover: background: #f5f5f5;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="contact-avatar" style="width: 40px; height: 40px; border-radius: 50%; background: #007bff; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                                    ${chat.contact_name.charAt(0).toUpperCase()}
                                </div>
                                <div style="flex: 1;">
                                    <div style="font-weight: bold; margin-bottom: 2px;">${chat.contact_name}</div>
                                    <div style="color: #666; font-size: 0.9em; truncate: ellipsis;">${chat.last_message || 'Nova conversa'}</div>
                                </div>
                                ${chat.unread_count > 0 ? `<div class="unread-badge" style="background: #007bff; color: white; border-radius: 50%; padding: 2px 6px; font-size: 0.8em;">${chat.unread_count}</div>` : ''}
                            </div>
                        </div>
                    `).join('');
                }
                
            } catch (error) {
                console.error('Erro ao carregar mensagens:', error);
                document.getElementById('chat-list').innerHTML = `
                    <div class="error-state">
                        <p>❌ Erro ao carregar conversas</p>
                        <button class="btn btn-sm btn-primary" onclick="loadMessages()">Tentar novamente</button>
                    </div>
                `;
            }
        }

        let currentChat = null;
        let messagesPollingInterval = null;

        async function openChat(phone, contactName, instanceId) {
            currentChat = { phone, contactName, instanceId };
            
            // Update active conversation
            document.querySelectorAll('.conversation-item').forEach(item => item.classList.remove('active'));
            
            // Update chat header with correct IDs
            const displayName = getContactDisplayName(contactName, phone);
            document.getElementById('chatContactName').textContent = displayName;
            document.getElementById('chatContactPhone').textContent = formatPhoneNumber(phone);
            document.getElementById('chatAvatar').textContent = getContactInitial(contactName, phone);
            
            // Show chat header and input area
            document.getElementById('chatHeader').classList.add('active');
            document.getElementById('messageInputArea').classList.add('active');
            
            // Load messages for this chat
            await loadChatMessages(phone, instanceId);
            
            // Start auto-refresh for this chat
            startMessagesAutoRefresh();
        }
        
        function startMessagesAutoRefresh() {
            // Clear existing interval
            if (messagesPollingInterval) {
                clearInterval(messagesPollingInterval);
            }
            
            // Start polling every 3 seconds
            messagesPollingInterval = setInterval(() => {
                if (currentChat) {
                    loadChatMessages(currentChat.phone, currentChat.instanceId);
                    loadConversations(); // Also refresh conversations list
                }
            }, 3000);
        }
        
        function stopMessagesAutoRefresh() {
            if (messagesPollingInterval) {
                clearInterval(messagesPollingInterval);
                messagesPollingInterval = null;
            }
        }
        
        async function loadChatMessages(phone, instanceId) {
            try {
                const response = await fetch(`/api/messages?phone=${phone}&instance_id=${instanceId}`);
                const messages = await response.json();
                
                const container = document.getElementById('messagesContainer');
                
                if (messages.length === 0) {
                    container.innerHTML = `
                        <div class="empty-chat-state">
                            <div class="empty-chat-icon">💭</div>
                            <h3>Nenhuma mensagem ainda</h3>
                            <p>Comece uma conversa!</p>
                        </div>
                    `;
                } else {
                    container.innerHTML = messages.map(msg => `
                        <div class="message-bubble ${msg.direction}">
                            <div class="message-content ${msg.direction}">
                                <div class="message-text">${msg.message}</div>
                                <div class="message-time">
                                    ${new Date(msg.created_at).toLocaleTimeString('pt-BR', { 
                                        hour: '2-digit', 
                                        minute: '2-digit' 
                                    })}
                                </div>
                            </div>
                        </div>
                    `).join('');
                    
                    container.scrollTop = container.scrollHeight;
                }
                
            } catch (error) {
                console.error('❌ Erro ao carregar mensagens:', error);
                document.getElementById('messagesContainer').innerHTML = `
                    <div class="empty-chat-state">
                        <div style="color: red;">❌ Erro ao carregar mensagens</div>
                    </div>
                `;
            }
        }

        async function sendWebhook() {
            if (!currentChat) {
                alert('❌ Selecione uma conversa primeiro');
                return;
            }
            
            const webhookUrl = prompt('URL do Webhook:', 'https://webhook.site/your-webhook-url');
            if (!webhookUrl) return;
            
            try {
                const chatData = {
                    contact_name: currentChat.contactName,
                    contact_phone: currentChat.phone,
                    instance_id: currentChat.instanceId,
                    timestamp: new Date().toISOString()
                };
                
                const response = await fetch('/api/webhooks/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: webhookUrl,
                        data: chatData
                    })
                });
                
                if (response.ok) {
                    alert('✅ Webhook enviado com sucesso!');
                } else {
                    alert('❌ Erro ao enviar webhook');
                }
                
            } catch (error) {
                console.error('Erro ao enviar webhook:', error);
                alert('❌ Erro de conexão');
            }
        }

        async function loadContacts() {
            try {
                const response = await fetch('/api/contacts');
                const contacts = await response.json();
                renderContacts(contacts);
            } catch (error) {
                console.error('Error loading contacts');
                document.getElementById('contacts-container').innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <div class="empty-title">Erro ao carregar contatos</div>
                        <p>Tente novamente em alguns instantes</p>
                    </div>
                `;
            }
        }

        function renderMessages(messages) {
            const container = document.getElementById('messages-container');
            if (!messages || messages.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">💬</div>
                        <div class="empty-title">Nenhuma mensagem ainda</div>
                        <p>As mensagens do WhatsApp aparecerão aqui quando começar a receber</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = messages.map(msg => `
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 10px 0;">
                    <div style="font-weight: 600;">${msg.from}</div>
                    <div style="color: #6b7280; font-size: 12px; margin: 5px 0;">${new Date(msg.timestamp).toLocaleString()}</div>
                    <div>${msg.message}</div>
                </div>
            `).join('');
        }

        function renderContacts(contacts) {
            const container = document.getElementById('contacts-container');
            if (!contacts || contacts.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">👥</div>
                        <div class="empty-title">Nenhum contato ainda</div>
                        <p>Os contatos aparecerão aqui quando começar a receber mensagens</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = contacts.map(contact => `
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #1f2937;">${contact.name}</div>
                        <div style="color: #6b7280; font-size: 14px;">📱 ${contact.phone}</div>
                        <div style="color: #9ca3af; font-size: 12px;">Adicionado: ${new Date(contact.created_at).toLocaleDateString()}</div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="startChat('${contact.phone}', '${contact.name}')" style="padding: 8px 12px; font-size: 12px;">💬 Conversar</button>
                    </div>
                </div>
            `).join('');
        }

        function startChat(phone, name) {
            const message = prompt(`💬 Enviar mensagem para ${name} (${phone}):`);
            if (message && message.trim()) {
                sendMessage(phone, message.trim());
            }
        }

        async function sendMessage(phone, message) {
            try {
                const response = await fetch('/api/whatsapp/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone_number: phone, message: message })
                });
                
                if (response.ok) {
                    alert('✅ Mensagem enviada com sucesso!');
                } else {
                    const error = await response.json();
                    alert(`❌ Erro ao enviar: ${error.error || 'Erro desconhecido'}`);
                }
            } catch (error) {
                console.error('Send error:', error);
                let errorMessage = 'Erro de conexão ao enviar mensagem';
                if (error.message.includes('fetch') || error instanceof TypeError) {
                    errorMessage = 'Serviço Baileys indisponível na porta 3002';
                }
                alert(`❌ ${errorMessage}`);
            }
        }

        async function checkConnectionStatus() {
            try {
                const response = await fetch('/api/whatsapp/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('connection-status');
                const userInfoEl = document.getElementById('connected-user-info');
                
                if (status.connected) {
                    statusEl.className = 'status-indicator status-connected';
                    statusEl.innerHTML = '<div class="status-dot"></div><span>WhatsApp conectado</span>';
                    
                    if (status.user) {
                        userInfoEl.style.display = 'block';
                        userInfoEl.innerHTML = `
                            <div class="connected-user">
                                <strong>👤 Usuário conectado:</strong><br>
                                📱 ${status.user.name || status.user.id}<br>
                                📞 ${status.user.id}
                            </div>
                        `;
                    }
                } else if (status.connecting) {
                    statusEl.className = 'status-indicator status-connecting';
                    statusEl.innerHTML = '<div class="status-dot"></div><span>Conectando WhatsApp...</span>';
                    userInfoEl.style.display = 'none';
                } else {
                    statusEl.className = 'status-indicator status-disconnected';
                    statusEl.innerHTML = '<div class="status-dot"></div><span>WhatsApp desconectado</span>';
                    userInfoEl.style.display = 'none';
                }
                
                // Update instances with connection status
                loadInstances();
                
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }

        async function startQRPolling() {
            const container = document.getElementById('qr-container');
            
            qrPollingInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/whatsapp/qr');
                    const data = await response.json();
                    
                    if (data.qr) {
                        container.innerHTML = `
                            <div class="qr-code">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(data.qr)}" 
                                     alt="QR Code WhatsApp" style="border-radius: 8px;">
                            </div>
                            <p style="margin-top: 15px; color: #10b981; font-weight: 500;">✅ QR Code real gerado! Escaneie com seu WhatsApp</p>
                        `;
                    } else if (data.connected) {
                        hideQRModal();
                        alert('🎉 WhatsApp conectado com sucesso!');
                        checkConnectionStatus();
                    } else {
                        container.innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 2rem; margin-bottom: 15px;">⏳</div>
                                <p>Aguardando QR Code...</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('Error polling QR:', error);
                }
            }, 2000);
        }

        function renderInstances() {
            const container = document.getElementById('instances-container');
            
            if (!instances || instances.length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">📱</div>
                        <div class="empty-title">Nenhuma instância</div>
                        <p>Crie sua primeira instância WhatsApp para começar</p>
                        <br>
                        <button class="btn btn-primary" onclick="showCreateModal()">🚀 Criar Primeira Instância</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = instances.map(instance => `
                <div class="instance-card ${instance.connected ? 'connected' : ''}">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <div>
                            <h3>${instance.name}</h3>
                            <small>ID: ${instance.id.substring(0, 8)}...</small>
                        </div>
                        <div class="status-indicator ${instance.connected ? 'status-connected' : 'status-disconnected'}">
                            <div class="status-dot"></div>
                            <span>${instance.connected ? 'Conectado' : 'Desconectado'}</span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">${instance.contacts_count || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Contatos</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">${instance.messages_today || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Mensagens</div>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        ${!instance.connected ? 
                            `<button class="btn btn-success" onclick="connectInstance('${instance.id}')" style="flex: 1;">🔗 Conectar Real</button>` :
                            `<button class="btn btn-secondary" disabled style="flex: 1;">✅ Conectado</button>`
                        }
                        <button class="btn btn-primary" onclick="showQRCode('${instance.id}')">📋 Ver QR Code</button>
                        <button class="btn btn-danger" onclick="disconnectInstance('${instance.id}')">❌ Desconectar</button>
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}', '${instance.name}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }

        
        // Messages and Instance Selection Functions
        
        async function loadInstancesForSelect() {
            try {
                const response = await fetch('/api/instances');
                const instances = await response.json();
                
                const select = document.getElementById('instanceSelect');
                select.innerHTML = '<option value="">Todas as instâncias</option>';
                
                instances.forEach(instance => {
                    const option = document.createElement('option');
                    option.value = instance.id;
                    option.textContent = `${instance.name} ${instance.connected ? '(Conectado)' : '(Desconectado)'}`;
                    select.appendChild(option);
                });
                
                // Load all conversations by default
                loadConversations();
                
            } catch (error) {
                console.error('❌ Erro ao carregar instâncias para seletor:', error);
            }
        }
        
        function switchInstance() {
            const select = document.getElementById('instanceSelect');
            currentInstanceId = select.value || null; // null means all instances
            
            console.log('📱 Instância selecionada:', currentInstanceId || 'Todas');
            loadConversations();
            clearCurrentChat();
        }
        
        async function loadConversations() {
            try {
                const url = currentInstanceId ? 
                    `/api/chats?instance_id=${currentInstanceId}` : 
                    '/api/chats';
                
                console.log('📥 Carregando conversas da URL:', url);
                
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const conversations = await response.json();
                
                console.log('📊 Conversas carregadas:', conversations.length);
                renderConversations(conversations);
                
            } catch (error) {
                console.error('❌ Erro ao carregar conversas:', error);
                
                const container = document.getElementById('conversationsList');
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <div class="empty-title">Erro ao carregar conversas</div>
                        <p>${error.message}</p>
                        <button class="btn btn-primary" onclick="loadConversations()">🔄 Tentar Novamente</button>
                    </div>
                `;
            }
        }
        
        function renderConversations(conversations) {
            const container = document.getElementById('conversationsList');
            
            if (!conversations || conversations.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">💬</div>
                        <div class="empty-title">Nenhuma conversa</div>
                        <p>${currentInstanceId ? 'Nenhuma conversa nesta instância' : 'As conversas aparecerão aqui quando receber mensagens'}</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = conversations.map(chat => {
                // Generate user avatar/photo
                const userInitial = getContactInitial(chat.contact_name, chat.contact_phone);
                const avatarColor = getAvatarColor(chat.contact_phone);
                
                return `
                    <div class="conversation-item" onclick="openChat('${chat.contact_phone}', '${chat.contact_name}', '${chat.instance_id}')">
                        <div class="conversation-avatar" style="background-color: ${avatarColor}">
                            ${userInitial}
                        </div>
                        <div class="conversation-info">
                            <div class="conversation-name">${getContactDisplayName(chat.contact_name, chat.contact_phone)}</div>
                            <div class="conversation-last-message">${chat.last_message || 'Nova conversa'}</div>
                        </div>
                        <div class="conversation-meta">
                            <div class="conversation-time">
                                ${chat.last_message_time ? new Date(chat.last_message_time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                            </div>
                            ${chat.unread_count > 0 ? `<div class="unread-badge">${chat.unread_count}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function getAvatarColor(phone) {
            // Generate consistent color based on phone number
            const colors = [
                '#4285f4', '#34a853', '#fbbc05', '#ea4335',
                '#9c27b0', '#673ab7', '#3f51b5', '#2196f3',
                '#00bcd4', '#009688', '#4caf50', '#8bc34a',
                '#cddc39', '#ffeb3b', '#ffc107', '#ff9800',
                '#ff5722', '#795548', '#607d8b', '#e91e63'
            ];
            
            let hash = 0;
            for (let i = 0; i < phone.length; i++) {
                hash = phone.charCodeAt(i) + ((hash << 5) - hash);
            }
            
            return colors[Math.abs(hash) % colors.length];
        }
        
        function getContactDisplayName(name, phone) {
            // Se o nome é um número de telefone ou está vazio, usar o número formatado
            if (!name || name === phone || /^\+?\d+$/.test(name)) {
                return formatPhoneNumber(phone);
            }
            return name;
        }
        
        function formatPhoneNumber(phone) {
            // Formatar número do telefone para exibição
            const cleaned = phone.replace(/\D/g, '');
            if (cleaned.length === 13 && cleaned.startsWith('55')) {
                return `+55 (${cleaned.substr(2, 2)}) ${cleaned.substr(4, 5)}-${cleaned.substr(9)}`;
            } else if (cleaned.length === 11) {
                return `(${cleaned.substr(0, 2)}) ${cleaned.substr(2, 5)}-${cleaned.substr(7)}`;
            }
            return phone;
        }
        
        function getContactInitial(name, phone) {
            if (name && name !== phone && !/^\+?\d+$/.test(name)) {
                return name.charAt(0).toUpperCase();
            }
            // Se é número de telefone, usar o último dígito
            const digits = phone.replace(/\D/g, '');
            return digits.slice(-1);
        }
        
        function searchConversations() {
            const query = document.getElementById('searchConversations').value.toLowerCase();
            const items = document.querySelectorAll('.conversation-item');
            
            items.forEach(item => {
                const name = item.querySelector('.conversation-name').textContent.toLowerCase();
                const message = item.querySelector('.conversation-last-message').textContent.toLowerCase();
                
                if (name.includes(query) || message.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        function clearCurrentChat() {
            currentChat = null;
            stopMessagesAutoRefresh(); // Stop auto-refresh when clearing chat
            document.getElementById('chatHeader').classList.remove('active');
            document.getElementById('messageInputArea').classList.remove('active');
            document.getElementById('messagesContainer').innerHTML = `
                <div class="empty-chat-state">
                    <div class="empty-chat-icon">💭</div>
                    <h3>Selecione uma conversa</h3>
                    <p>Escolha uma conversa da lista para visualizar mensagens</p>
                </div>
            `;
        }
        
        function handleMessageKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        async function sendMessage() {
            if (!currentChat) {
                alert('❌ Selecione uma conversa primeiro');
                return;
            }
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) {
                alert('❌ Digite uma mensagem primeiro');
                return;
            }
            
            // Show sending indicator
            messageInput.disabled = true;
            const sendButton = document.querySelector('#messageInputArea .btn-success');
            const originalText = sendButton.textContent;
            sendButton.textContent = '📤 Enviando...';
            sendButton.disabled = true;
            
            try {
                console.log('📤 Enviando mensagem para:', currentChat.phone, 'via instância:', currentChat.instanceId);
                
                // Check backend health before sending
                const healthResponse = await fetch('/api/whatsapp/health');

                if (!healthResponse.ok) {
                    throw new Error('Serviço Baileys não está disponível');
                }

                // Send via backend which proxies to Baileys
                const response = await fetch('/api/whatsapp/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        phone_number: currentChat.phone,
                        message: message,
                        device_id: currentChat.instanceId
                    })
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    let errorData;
                    try {
                        errorData = JSON.parse(errorText);
                    } catch (e) {
                        throw new Error(`HTTP ${response.status}: ${errorText}`);
                    }
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                console.log('📤 Resposta do envio:', result);
                
                if (result.success) {
                    messageInput.value = '';
                    
                    // Add message to UI immediately for better UX
                    const container = document.getElementById('messagesContainer');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message-bubble outgoing';
                    messageDiv.innerHTML = `
                        <div class="message-content outgoing">
                            <div class="message-text">${message}</div>
                            <div class="message-time">
                                ${new Date().toLocaleTimeString('pt-BR', { 
                                    hour: '2-digit', 
                                    minute: '2-digit' 
                                })}
                            </div>
                        </div>
                    `;
                    container.appendChild(messageDiv);
                    container.scrollTop = container.scrollHeight;
                    
                    console.log('✅ Mensagem enviada com sucesso');
                    
                    // Refresh conversations list to update last message
                    setTimeout(() => loadConversations(), 1000);
                    
                } else {
                    throw new Error(result.error || 'Erro desconhecido ao enviar mensagem');
                }
                
            } catch (error) {
                console.error('❌ Erro ao enviar mensagem:', error);
                
                let errorMessage = error.message;
                
                if (errorMessage.includes('fetch')) {
                    errorMessage = 'Serviço Baileys indisponível na porta 3002';
                } else if (errorMessage.includes('não conectada') || errorMessage.includes('não encontrada')) {
                    errorMessage = 'A instância não está conectada ao WhatsApp. Conecte primeiro na aba Instâncias.';
                } else if (errorMessage.includes('timeout')) {
                    errorMessage = 'Timeout ao enviar mensagem. Tente novamente.';
                }
                
                alert(`❌ ${errorMessage}`);
                
            } finally {
                // Restore button state
                messageInput.disabled = false;
                sendButton.textContent = originalText;
                sendButton.disabled = false;
                messageInput.focus();
            }
        }
        
        function refreshMessages() {
            loadConversations();
            if (currentChat) {
                loadChatMessages(currentChat.phone, currentChat.instanceId);
            }
        }
        
        async function sendWebhook() {
            if (!currentChat) {
                alert('❌ Selecione uma conversa primeiro');
                return;
            }
            
            const webhookUrl = prompt('URL do Webhook:', 'https://webhook.site/your-webhook-url');
            if (!webhookUrl) return;
            
            try {
                const chatData = {
                    contact_name: currentChat.contactName,
                    contact_phone: currentChat.phone,
                    instance_id: currentChat.instanceId,
                    timestamp: new Date().toISOString()
                };
                
                const response = await fetch('/api/webhooks/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: webhookUrl,
                        data: chatData
                    })
                });
                
                if (response.ok) {
                    alert('✅ Webhook enviado com sucesso!');
                } else {
                    alert('❌ Erro ao enviar webhook');
                }
                
            } catch (error) {
                console.error('❌ Erro ao enviar webhook:', error);
                alert('❌ Erro de conexão');
            }
        }
        
        // Flow Creator Functions
        async function createNewFlow() {
            const flowName = prompt('Nome do novo fluxo:', 'Meu Fluxo de Automação');
            if (!flowName) return;
            
            const flowDescription = prompt('Descrição do fluxo (opcional):', 'Fluxo de resposta automática');
            
            try {
                const response = await fetch('/api/flows', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: flowName,
                        description: flowDescription || '',
                        nodes: [
                            {
                                id: 'start',
                                type: 'start',
                                position: { x: 100, y: 100 },
                                data: { label: 'Início' }
                            }
                        ],
                        edges: [],
                        active: false
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert(`✅ Fluxo "${flowName}" criado com sucesso!`);
                    loadFlows();
                } else {
                    alert('❌ Erro ao criar fluxo');
                }
                
            } catch (error) {
                console.error('❌ Erro ao criar fluxo:', error);
                alert('❌ Erro de conexão');
            }
        }
        
        async function loadFlows() {
            try {
                const response = await fetch('/api/flows');
                const flows = await response.json();
                renderFlows(flows);
            } catch (error) {
                console.error('❌ Erro ao carregar fluxos:', error);
                document.getElementById('flows-container').innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <div class="empty-title">Erro ao carregar fluxos</div>
                    </div>
                `;
            }
        }
        
        function renderFlows(flows) {
            const container = document.getElementById('flows-container');
            
            if (!flows || flows.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🎯</div>
                        <div class="empty-title">Nenhum fluxo criado ainda</div>
                        <p>Crie fluxos de automação para otimizar seu atendimento</p>
                        <br>
                        <button class="btn btn-primary" onclick="createNewFlow()">
                            🚀 Criar Primeiro Fluxo
                        </button>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = `
                <div class="flows-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                    ${flows.map(flow => `
                        <div class="flow-card" style="background: white; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                                <div>
                                    <h3 style="margin: 0 0 0.5rem 0; font-size: 1.125rem; font-weight: 600;">${flow.name}</h3>
                                    <p style="margin: 0; color: #6b7280; font-size: 0.875rem;">${flow.description || 'Sem descrição'}</p>
                                </div>
                                <div style="padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600; ${flow.active ? 'background: rgba(16, 185, 129, 0.1); color: #059669;' : 'background: rgba(239, 68, 68, 0.1); color: #dc2626;'}">
                                    ${flow.active ? 'Ativo' : 'Inativo'}
                                </div>
                            </div>
                            
                            <div style="margin: 1rem 0; padding: 1rem; background: #f9fafb; border-radius: 0.5rem;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <span style="font-size: 0.8rem; color: #6b7280;">Nós:</span>
                                    <span style="font-weight: 600;">${flow.nodes ? flow.nodes.length : 0}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <span style="font-size: 0.8rem; color: #6b7280;">Criado:</span>
                                    <span style="font-size: 0.8rem;">${new Date(flow.created_at).toLocaleDateString('pt-BR')}</span>
                                </div>
                            </div>
                            
                            <div style="display: flex; gap: 0.5rem;">
                                <button class="btn btn-sm btn-primary" onclick="editFlow('${flow.id}')">
                                    ✏️ Editar
                                </button>
                                <button class="btn btn-sm ${flow.active ? 'btn-secondary' : 'btn-success'}" onclick="toggleFlow('${flow.id}', ${flow.active})">
                                    ${flow.active ? '⏸️ Pausar' : '▶️ Ativar'}
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteFlow('${flow.id}', '${flow.name}')">
                                    🗑️ Excluir
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function editFlow(flowId) {
            alert(`🚧 Editor de Fluxos em Desenvolvimento!\n\nFluxo ID: ${flowId}\n\nEm breve você poderá editar fluxos com interface drag-and-drop.\n\nFuncionalidades planejadas:\n• Editor visual\n• Nós de condição\n• Nós de resposta\n• Nós de delay\n• Integração com instâncias`);
        }
        
        async function toggleFlow(flowId, currentStatus) {
            try {
                const response = await fetch(`/api/flows/${flowId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        active: !currentStatus
                    })
                });
                
                if (response.ok) {
                    loadFlows();
                } else {
                    alert('❌ Erro ao alterar status do fluxo');
                }
            } catch (error) {
                console.error('❌ Erro ao alterar fluxo:', error);
                alert('❌ Erro de conexão');
            }
        }
        
        async function deleteFlow(flowId, flowName) {
            if (!confirm(`Excluir fluxo "${flowName}"?\n\nEsta ação não pode ser desfeita.`)) return;
            
            try {
                const response = await fetch(`/api/flows/${flowId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert(`✅ Fluxo "${flowName}" excluído com sucesso!`);
                    loadFlows();
                } else {
                    alert('❌ Erro ao excluir fluxo');
                }
            } catch (error) {
                console.error('❌ Erro ao excluir fluxo:', error);
                alert('❌ Erro de conexão');
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            checkConnectionStatus();
            loadInstancesForSelect(); // Load instances for message selector
            
            // Start status polling
            statusPollingInterval = setInterval(checkConnectionStatus, 5000);
            
            // Update stats every 30 seconds
            setInterval(loadStats, 30000);
            
            document.getElementById('createModal').addEventListener('click', function(e) {
                if (e.target === this) this.classList.remove('show');
            });
            
            document.getElementById('qrModal').addEventListener('click', function(e) {
                if (e.target === this) closeQRModal();
            });
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            if (qrPollingInterval) clearInterval(qrPollingInterval);
            if (statusPollingInterval) clearInterval(statusPollingInterval);
        });
        
        // Schedule Management Functions
        async function loadInstancesForSchedule() {
            try {
                const response = await fetch('/api/instances');
                const instances = await response.json();
                const select = document.getElementById('scheduleInstanceSelect');
                select.innerHTML = '<option value="">Selecione uma instância</option>';
                instances.forEach(instance => {
                    const option = document.createElement('option');
                    option.value = instance.id;
                    const status = instance.connected ? '(Conectado)' : '(Desconectado)';
                    option.textContent = `${instance.name} ${status}`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('❌ Erro ao carregar instâncias:', error);
            }
        }

        async function loadGroupsForSchedule() {
            const instanceId = document.getElementById('scheduleInstanceSelect').value;
            const select = document.getElementById('scheduleGroupSelect');
            select.innerHTML = '<option value="">Carregando...</option>';
            if (!instanceId) {
                select.innerHTML = '<option value="">Selecione uma instância</option>';
                return;
            }
            try {
                const response = await fetch(`/api/groups/${instanceId}`);
                const result = await response.json();
                select.innerHTML = '<option value="">Selecione um grupo</option>';
                (result.groups || []).forEach(group => {
                    const option = document.createElement('option');
                    option.value = group.id;
                    option.textContent = group.name || `Grupo ${group.id.split('@')[0]}`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('❌ Erro ao carregar grupos:', error);
                select.innerHTML = '<option value="">Erro ao carregar</option>';
            }
        }

        function openScheduleModal() {
            loadInstancesForSchedule();
            document.getElementById('scheduleModal').style.display = 'block';
        }

        function closeScheduleModal() {
            document.getElementById('scheduleModal').style.display = 'none';
        }

        function toggleMediaInput() {
            const type = document.getElementById('messageType').value;
            const fileInput = document.getElementById('scheduleMedia');
            if (type === 'text') {
                fileInput.style.display = 'none';
            } else {
                fileInput.style.display = 'block';
            }
        }

        async function submitSchedule() {
            const instanceId = document.getElementById('scheduleInstanceSelect').value;
            const groupId = document.getElementById('scheduleGroupSelect').value;
            const content = document.getElementById('scheduleText').value;
            const mediaType = document.getElementById('messageType').value;
            const weekday = document.getElementById('weekdaySelect').value;
            const time = document.getElementById('scheduleTime').value;
            const file = document.getElementById('scheduleMedia').files[0];

            if (!instanceId || !groupId || !time) {
                alert('❌ Preencha todos os campos obrigatórios');
                return;
            }

            const formData = new FormData();
            formData.append('instance_id', instanceId);
            formData.append('group_id', groupId);
            formData.append('content', content);
            formData.append('media_type', mediaType);
            formData.append('weekday', weekday);
            formData.append('send_time', time);
            formData.append('recurrence', 'weekly');
            if (file) formData.append('media', file);

            const response = await fetch('/api/messages/schedule', { method: 'POST', body: formData });
            const result = await response.json();
            if (response.ok && result.success) {
                loadScheduledMessages();
                closeScheduleModal();
            } else {
                alert('❌ Erro ao agendar mensagem');
            }
        }

        async function loadScheduledMessages() {
            const selectedDay = document.getElementById('previewWeekday')?.value || '';
            try {
                const response = await fetch('/api/messages/scheduled');
                const result = await response.json();
                const container = document.getElementById('scheduledMessages');
                container.innerHTML = '';
                const messages = Array.isArray(result) ? result.filter(item => selectedDay === '' || String(item.weekday) === selectedDay) : [];
                if (messages.length === 0) {
                    container.innerHTML = '<div class="empty-state"><p>Nenhuma mensagem agendada</p></div>';
                    return;
                }
                messages.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'scheduled-card';
                    div.innerHTML = `
                        <div class="scheduled-info">
                            <strong>${item.group_id}</strong>
                            <span>${item.send_time}</span>
                        </div>
                        <button class="btn btn-sm btn-danger" onclick="deleteSchedule('${item.id}')">❌</button>
                    `;
                    container.appendChild(div);
                });
            } catch (error) {
                console.error('❌ Erro ao carregar mensagens agendadas:', error);
            }
        }

        async function deleteSchedule(id) {
            await fetch('/api/messages/scheduled/' + id, { method: 'DELETE' });
            loadScheduledMessages();
        }

        async function loadCampaigns() {
            try {
                const res = await fetch('/api/campaigns');
                const campaigns = await res.json();
                const list = document.getElementById('campaignList');
                const sel = document.getElementById('scheduleCampaign');
                list.innerHTML = '';
                sel.innerHTML = '';
                campaigns.forEach(c => {
                    const div = document.createElement('div');
                    div.textContent = c.name;
                    list.appendChild(div);
                    const opt = document.createElement('option');
                    opt.value = c.id;
                    opt.textContent = c.name;
                    sel.appendChild(opt);
                });
            } catch (err) {
                console.error('Erro ao carregar campanhas', err);
            }
        }

        async function createCampaign(ev) {
            ev.preventDefault();
            const payload = {
                name: document.getElementById('campName').value,
                description: document.getElementById('campDesc').value,
                recurrence: document.getElementById('campRecurrence').value,
                send_time: document.getElementById('campTime').value,
                weekday: document.getElementById('campWeekday').value || null
            };
            await fetch('/api/campaigns', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            loadCampaigns();
            document.getElementById('campaignForm').reset();
        }

        async function loadGroupsForSchedule() {
            try {
                const res = await fetch('/api/groups/default');
                const groups = await res.json();
                const sel = document.getElementById('scheduleGroups');
                sel.innerHTML = '';
                groups.forEach(g => {
                    const opt = document.createElement('option');
                    opt.value = g.id || g.groupId || g;
                    opt.textContent = g.name || g.subject || g.id || g;
                    sel.appendChild(opt);
                });
            } catch (err) {
                console.error('Erro ao carregar grupos', err);
            }
        }

        async function scheduleMessage(ev) {
            ev.preventDefault();
            const campaign = document.getElementById('scheduleCampaign').value;
            const groups = Array.from(document.getElementById('scheduleGroups').selectedOptions).map(o => o.value);
            const payload = {
                campaign_id: campaign,
                groups: groups,
                content: document.getElementById('scheduleContent').value,
                media_type: document.getElementById('scheduleMediaType').value,
                media_path: document.getElementById('scheduleMediaPath').value
            };
            await fetch('/api/messages/schedule', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            loadScheduledList();
            document.getElementById('scheduleForm').reset();
        }

        async function loadScheduledList() {
            const res = await fetch('/api/messages/scheduled');
            const data = await res.json();
            const container = document.getElementById('scheduledList');
            container.innerHTML = '';
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'scheduled-card';
                div.innerHTML = `<strong>${item.campaign_name}</strong> - ${item.next_run} <button class="btn btn-sm btn-danger" onclick="deleteScheduled('${item.id}')">❌</button>`;
                container.appendChild(div);
            });
        }

        async function deleteScheduled(id) {
            await fetch('/api/messages/scheduled/' + id, { method: 'DELETE' });
            loadScheduledList();
        }

        document.getElementById('previewWeekday').value = new Date().getDay();
        loadScheduledMessages();
        loadCampaigns();
        loadGroupsForSchedule();
        loadScheduledList();
    </script>
</body>
</html>'''


# Database setup (same as before but with WebSocket integration)
def init_db():
    """Initialize SQLite database with WAL mode for better concurrency"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA cache_size = 1000")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB
    
    # Enhanced tables with better schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            connected INTEGER DEFAULT 0,
            user_name TEXT,
            user_id TEXT,
            contacts_count INTEGER DEFAULT 0,
            messages_today INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            instance_id TEXT DEFAULT 'default',
            avatar_url TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            contact_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            direction TEXT NOT NULL,
            instance_id TEXT DEFAULT 'default',
            message_type TEXT DEFAULT 'text',
            whatsapp_id TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            contact_phone TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            instance_id TEXT NOT NULL,
            last_message TEXT,
            last_message_time TEXT,
            unread_count INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            nodes TEXT NOT NULL,
            edges TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            instance_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            recurrence TEXT,
            send_time TEXT,
            weekday INTEGER,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_groups (
            campaign_id TEXT NOT NULL,
            group_id TEXT NOT NULL,
            PRIMARY KEY (campaign_id, group_id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_groups_campaign_id ON campaign_groups(campaign_id)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_messages (
            id TEXT PRIMARY KEY,
            campaign_id TEXT NOT NULL,
            content TEXT,
            media_type TEXT DEFAULT 'text',
            media_path TEXT,
            next_run TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_next_run ON scheduled_messages(next_run)")
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com suporte WebSocket")

def send_via_baileys(phone: str, message: str, instance_id: str = "default") -> bool:
    """Send a WhatsApp message using the local Baileys service."""
    to = phone if phone.endswith("@s.whatsapp.net") or phone.endswith("@c.us") else f"{phone}@s.whatsapp.net"
    data = {"to": to, "message": message, "type": "text"}
    success = False
    try:
        import requests  # type: ignore
        try:
            response = requests.post(f"http://127.0.0.1:3002/send/{instance_id}", json=data, timeout=10)
            success = response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    except ImportError:
        import urllib.request
        req_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:3002/send/{instance_id}",
            data=req_data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                success = response.status == 200
        except Exception:
            return False

    if success:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        message_id = str(uuid.uuid4())
        phone_clean = to.replace("@s.whatsapp.net", "").replace("@c.us", "")
        cursor.execute(
            """
            INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                f"Para {phone_clean[-4:]}",
                phone_clean,
                message,
                "outgoing",
                instance_id,
                datetime.now(BR_TZ).astimezone(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        conn.close()
    return success


def baileys_post(url: str, data: Dict[str, Any]) -> None:
    import requests  # type: ignore
    requests.post(url, json=data, timeout=10)


def send_scheduled_message(group_id: str, content: str, media_type: str, media_path: str, instance_id: str = "default") -> bool:
    """Send a scheduled message including optional media."""
    data = {"to": group_id, "type": media_type or "text", "message": content or ""}
    if media_type and media_type != "text" and media_path:
        try:
            with open(media_path, "rb") as f:
                data[media_type] = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return False
    try:
        baileys_post(f"http://127.0.0.1:{BAILEYS_PORT}/send/{instance_id}", data)
        return True
    except Exception:
        return False


def calculate_next_run(recurrence: str, send_time: str, weekday: int | None = None, base_dt: datetime | None = None) -> str:
    """Calculate next run datetime based on recurrence."""
    now = base_dt or datetime.now(BR_TZ)
    if now.tzinfo is None:
        now = now.replace(tzinfo=BR_TZ)
    if recurrence == "once":
        return send_time
    hour, minute = map(int, send_time.split(":"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if recurrence == "daily":
        if target <= now:
            target += timedelta(days=1)
    elif recurrence == "weekly" and weekday is not None:
        days_ahead = (weekday - now.weekday()) % 7
        target = target + timedelta(days=days_ahead)
        if target <= now:
            target += timedelta(days=7)
    return target.astimezone(timezone.utc).isoformat()


def process_scheduled_messages(now: datetime | None = None) -> None:
    """Process due scheduled messages once."""
    current = now or datetime.now(BR_TZ)
    if current.tzinfo is None:
        current = current.replace(tzinfo=BR_TZ)
    current_utc = current.astimezone(timezone.utc)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT sm.*, c.recurrence, c.send_time, c.weekday
        FROM scheduled_messages sm
        JOIN campaigns c ON c.id = sm.campaign_id
        WHERE sm.next_run <= ? AND sm.status = 'pending'
        """,
        (current_utc.isoformat(),),
    )
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute(
            "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
            (row["campaign_id"],),
        )
        groups = [g[0] for g in cursor.fetchall()]
        for group_id in groups:
            send_scheduled_message(group_id, row["content"], row["media_type"], row["media_path"])
        if row["recurrence"] == "once":
            cursor.execute(
                "UPDATE scheduled_messages SET status = 'sent' WHERE id = ?",
                (row["id"],),
            )
        else:
            next_run = calculate_next_run(
                row["recurrence"], row["send_time"], row["weekday"], base_dt=current
            )
            cursor.execute(
                "UPDATE scheduled_messages SET next_run = ? WHERE id = ?",
                (next_run, row["id"]),
            )
    conn.commit()
    conn.close()


async def scheduled_message_scheduler():
    while True:
        try:
            process_scheduled_messages()
        except Exception as e:
            logger.error(f"Erro no agendador de mensagens: {e}")
        await asyncio.sleep(60)


# WebSocket Server Functions
if WEBSOCKETS_AVAILABLE:
    async def websocket_handler(websocket, path):
        """Handle WebSocket connections"""
        websocket_clients.add(websocket)
        logger.info(f"📱 Cliente WebSocket conectado. Total: {len(websocket_clients)}")
        
        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            websocket_clients.discard(websocket)
            logger.info(f"📱 Cliente WebSocket desconectado. Total: {len(websocket_clients)}")

    async def broadcast_message(message_data: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not websocket_clients:
            return
        
        message = json.dumps(message_data)
        disconnected_clients = set()
        
        for client in websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem WebSocket: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            websocket_clients.discard(client)

    async def _websocket_server():
        async with websockets.serve(
            websocket_handler,
            "0.0.0.0",
            WEBSOCKET_PORT,
            ping_interval=30,
            ping_timeout=10,
        ):
            logger.info(f"🔌 WebSocket server iniciado na porta {WEBSOCKET_PORT}")
            await asyncio.Future()  # run forever

    def start_websocket_server():
        """Start WebSocket server in a separate thread"""

        def run_websocket():
            try:
                asyncio.run(_websocket_server())
            except Exception as e:
                logger.error(f"❌ Erro no WebSocket server: {e}")

        websocket_thread = threading.Thread(target=run_websocket, daemon=True)
        websocket_thread.start()
        return websocket_thread
else:
    def start_websocket_server():
        print("⚠️ WebSocket não disponível - modo básico")
        return None


def add_sample_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    current_time = datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()
    
    # Sample instance
    instance_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO instances (id, name, contacts_count, messages_today, created_at) VALUES (?, ?, ?, ?, ?)",
                  (instance_id, "WhatsApp Principal", 0, 0, current_time))
    
    conn.commit()
    conn.close()

# Baileys Service Manager
class BaileysManager:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.baileys_dir = "baileys_service"
        
    def start_baileys(self):
        """Start Baileys service"""
        if self.is_running:
            return True
            
        try:
            print("📦 Configurando serviço Baileys...")
            
            # Create Baileys service directory
            if not os.path.exists(self.baileys_dir):
                os.makedirs(self.baileys_dir)
                print(f"✅ Diretório {self.baileys_dir} criado")
            
            # Create package.json
            package_json = {
                "name": "whatsflow-baileys",
                "version": "1.0.0",
                "description": "WhatsApp Baileys Service for WhatsFlow",
                "main": "server.js",
                "dependencies": {
                    "@whiskeysockets/baileys": "^6.7.0",
                    "express": "^4.18.2",
                    "cors": "^2.8.5",
                    "qrcode-terminal": "^0.12.0"
                },
                "scripts": {
                    "start": "node server.js"
                }
            }
            
            package_path = f"{self.baileys_dir}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            print("✅ package.json criado")
            
            # Create Baileys server
            baileys_server = '''const express = require('express');
const cors = require('cors');
const { DisconnectReason, useMultiFileAuthState, downloadMediaMessage } = require('@whiskeysockets/baileys');
const makeWASocket = require('@whiskeysockets/baileys').default;
const qrTerminal = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors({
    origin: ['http://localhost:8889', 'http://127.0.0.1:8889', 'http://localhost:3000', 'http://127.0.0.1:3000'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Accept']
}));
app.use(express.json());

// Global state management
let instances = new Map(); // instanceId -> { sock, qr, connected, connecting, user }
let currentQR = null;
let qrUpdateInterval = null;

// QR Code auto-refresh every 30 seconds (WhatsApp QR expires after 60s)
const startQRRefresh = (instanceId) => {
    if (qrUpdateInterval) clearInterval(qrUpdateInterval);
    
    qrUpdateInterval = setInterval(() => {
        const instance = instances.get(instanceId);
        if (instance && !instance.connected && instance.connecting) {
            console.log('🔄 QR Code expirado, gerando novo...');
            // Don't reconnect immediately, let WhatsApp generate new QR
        }
    }, 30000); // 30 seconds
};

const stopQRRefresh = () => {
    if (qrUpdateInterval) {
        clearInterval(qrUpdateInterval);
        qrUpdateInterval = null;
    }
};

async function connectInstance(instanceId) {
    try {
        console.log(`🔄 Iniciando conexão para instância: ${instanceId}`);
        
        // Create instance directory
        const authDir = `./auth_${instanceId}`;
        if (!fs.existsSync(authDir)) {
            fs.mkdirSync(authDir, { recursive: true });
        }
        
        const { state, saveCreds } = await useMultiFileAuthState(authDir);
        
        const sock = makeWASocket({
            auth: state,
            browser: ['WhatsFlow', 'Desktop', '1.0.0'],
            connectTimeoutMs: 60000,
            defaultQueryTimeoutMs: 0,
            keepAliveIntervalMs: 30000,
            generateHighQualityLinkPreview: true,
            markOnlineOnConnect: true,
            syncFullHistory: true,
            retryRequestDelayMs: 5000,
            maxRetries: 5
        });

        // Initialize instance
        instances.set(instanceId, {
            sock: sock,
            qr: null,
            connected: false,
            connecting: true,
            user: null,
            lastSeen: new Date()
        });

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            const instance = instances.get(instanceId);
            
            if (qr) {
                console.log(`📱 Novo QR Code gerado para instância: ${instanceId}`);
                currentQR = qr;
                instance.qr = qr;
                
                // Manual QR display in terminal (since printQRInTerminal is deprecated)
                try {
                    qrTerminal.generate(qr, { small: true });
                } catch (err) {
                    console.log('⚠️ QR Terminal não disponível:', err.message);
                }
                
                startQRRefresh(instanceId);
            }
            
            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                const reason = lastDisconnect?.error?.output?.statusCode || 'unknown';
                
                console.log(`🔌 Instância ${instanceId} desconectada. Razão: ${reason}, Reconectar: ${shouldReconnect}`);
                
                instance.connected = false;
                instance.connecting = false;
                instance.user = null;
                stopQRRefresh();
                
                // Implement robust reconnection logic
                if (shouldReconnect) {
                    if (reason === DisconnectReason.restartRequired) {
                        console.log(`🔄 Restart requerido para ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 5000);
                    } else if (reason === DisconnectReason.connectionClosed) {
                        console.log(`🔄 Conexão fechada, reconectando ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 10000);
                    } else if (reason === DisconnectReason.connectionLost) {
                        console.log(`🔄 Conexão perdida, reconectando ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 15000);
                    } else if (reason === DisconnectReason.timedOut) {
                        console.log(`⏱️ Timeout, reconectando ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 20000);
                    } else {
                        console.log(`🔄 Reconectando ${instanceId} em 30 segundos`);
                        setTimeout(() => connectInstance(instanceId), 30000);
                    }
                } else {
                    console.log(`❌ Instância ${instanceId} deslogada permanentemente`);
                    // Clean auth files if logged out
                    try {
                        const authPath = path.join('./auth_' + instanceId);
                        if (fs.existsSync(authPath)) {
                            fs.rmSync(authPath, { recursive: true, force: true });
                            console.log(`🧹 Arquivos de auth removidos para ${instanceId}`);
                        }
                    } catch (err) {
                        console.log('⚠️ Erro ao limpar arquivos de auth:', err.message);
                    }
                }
                
                // Notify backend about disconnection
                try {
                    const fetch = (await import('node-fetch')).default;
                    await fetch('http://localhost:8889/api/whatsapp/disconnected', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            instanceId: instanceId,
                            reason: reason
                        })
                    });
                } catch (err) {
                    console.log('⚠️ Não foi possível notificar desconexão:', err.message);
                }
                
            } else if (connection === 'open') {
                console.log(`✅ Instância ${instanceId} conectada com SUCESSO!`);
                instance.connected = true;
                instance.connecting = false;
                instance.qr = null;
                instance.lastSeen = new Date();
                currentQR = null;
                stopQRRefresh();
                
                // Get user info
                instance.user = {
                    id: sock.user.id,
                    name: sock.user.name || sock.user.id.split(':')[0],
                    profilePictureUrl: null,
                    phone: sock.user.id.split(':')[0]
                };
                
                console.log(`👤 Usuário conectado: ${instance.user.name} (${instance.user.phone})`);
                
                // Try to get profile picture
                try {
                    const profilePic = await sock.profilePictureUrl(sock.user.id, 'image');
                    instance.user.profilePictureUrl = profilePic;
                    console.log('📸 Foto do perfil obtida');
                } catch (err) {
                    console.log('⚠️ Não foi possível obter foto do perfil');
                }
                
                // Wait a bit before importing chats to ensure connection is stable
                setTimeout(async () => {
                    try {
                        console.log('📥 Importando conversas existentes...');
                        
                        // Get all chats
                        const chats = await sock.getChats();
                        console.log(`📊 ${chats.length} conversas encontradas`);
                        
                        // Process chats in batches to avoid overwhelming the system
                        const batchSize = 20;
                        for (let i = 0; i < chats.length; i += batchSize) {
                            const batch = chats.slice(i, i + batchSize);
                            
                            // Send batch to Python backend
                            const fetch = (await import('node-fetch')).default;
                            await fetch('http://localhost:8889/api/chats/import', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    instanceId: instanceId,
                                    chats: batch,
                                    user: instance.user,
                                    batchNumber: Math.floor(i / batchSize) + 1,
                                    totalBatches: Math.ceil(chats.length / batchSize)
                                })
                            });
                            
                            console.log(`📦 Lote ${Math.floor(i / batchSize) + 1}/${Math.ceil(chats.length / batchSize)} enviado`);
                            
                            // Small delay between batches
                            await new Promise(resolve => setTimeout(resolve, 1000));
                        }
                        
                        console.log('✅ Importação de conversas concluída');
                        
                    } catch (err) {
                        console.log('⚠️ Erro ao importar conversas:', err.message);
                    }
                }, 5000); // Wait 5 seconds after connection
                
                // Send connected notification to Python backend
                setTimeout(async () => {
                    try {
                        const fetch = (await import('node-fetch')).default;
                        await fetch('http://localhost:8889/api/whatsapp/connected', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                instanceId: instanceId,
                                user: instance.user,
                                connectedAt: new Date().toISOString()
                            })
                        });
                        console.log('✅ Backend notificado sobre a conexão');
                    } catch (err) {
                        console.log('⚠️ Erro ao notificar backend:', err.message);
                    }
                }, 2000);
                
            } else if (connection === 'connecting') {
                console.log(`🔄 Conectando instância ${instanceId}...`);
                instance.connecting = true;
                instance.lastSeen = new Date();
            }
        });

        sock.ev.on('creds.update', saveCreds);
        
        // Handle incoming messages with better error handling
        sock.ev.on('messages.upsert', async (m) => {
            const messages = m.messages;
            
            for (const message of messages) {
                if (!message.key.fromMe && message.message) {
                    const from = message.key.remoteJid;
                    const messageText = message.message.conversation || 
                                      message.message.extendedTextMessage?.text || 
                                      'Mídia recebida';
                    
                    // Extract contact name from WhatsApp
                    const pushName = message.pushName || '';
                    const contact = await sock.onWhatsApp(from);
                    const contactName = pushName || contact[0]?.name || '';
                    
                    console.log(`📥 Nova mensagem na instância ${instanceId}`);
                    console.log(`👤 Contato: ${contactName || from.split('@')[0]} (${from.split('@')[0]})`);
                    console.log(`💬 Mensagem: ${messageText.substring(0, 50)}...`);
                    
                    // Send to Python backend with retry logic
                    let retries = 3;
                    while (retries > 0) {
                        try {
                            const fetch = (await import('node-fetch')).default;
                            const response = await fetch('http://localhost:8889/api/messages/receive', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    instanceId: instanceId,
                                    from: from,
                                    message: messageText,
                                    pushName: pushName,
                                    contactName: contactName,
                                    timestamp: new Date().toISOString(),
                                    messageId: message.key.id,
                                    messageType: message.message.conversation ? 'text' : 'media'
                                })
                            });
                            
                            if (response.ok) {
                                break; // Success, exit retry loop
                            } else {
                                throw new Error(`HTTP ${response.status}`);
                            }
                        } catch (err) {
                            retries--;
                            console.log(`❌ Erro ao enviar mensagem (tentativas restantes: ${retries}):`, err.message);
                            if (retries > 0) {
                                await new Promise(resolve => setTimeout(resolve, 2000));
                            }
                        }
                    }
                }
            }
        });

        // Keep connection alive with heartbeat
        setInterval(() => {
            const instance = instances.get(instanceId);
            if (instance && instance.connected && instance.sock) {
                instance.lastSeen = new Date();
                // Send heartbeat
                instance.sock.sendPresenceUpdate('available').catch(() => {});
            }
        }, 60000); // Every minute

    } catch (error) {
        console.error(`❌ Erro fatal ao conectar instância ${instanceId}:`, error);
        const instance = instances.get(instanceId);
        if (instance) {
            instance.connecting = false;
            instance.connected = false;
        }
    }
}

// API Routes with better error handling
app.get('/status/:instanceId?', (req, res) => {
    const { instanceId } = req.params;
    
    if (instanceId) {
        const instance = instances.get(instanceId);
        if (instance) {
            res.json({
                connected: instance.connected,
                connecting: instance.connecting,
                user: instance.user,
                instanceId: instanceId,
                lastSeen: instance.lastSeen
            });
        } else {
            res.json({
                connected: false,
                connecting: false,
                user: null,
                instanceId: instanceId,
                lastSeen: null
            });
        }
    } else {
        // Return all instances
        const allInstances = {};
        for (const [id, instance] of instances) {
            allInstances[id] = {
                connected: instance.connected,
                connecting: instance.connecting,
                user: instance.user,
                lastSeen: instance.lastSeen
            };
        }
        res.json(allInstances);
    }
});

app.get('/qr/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    const instance = instances.get(instanceId);
    
    if (instance && instance.qr) {
        res.json({
            qr: instance.qr,
            connected: instance.connected,
            instanceId: instanceId,
            expiresIn: 60 // QR expires in 60 seconds
        });
    } else {
        res.json({
            qr: null,
            connected: instance ? instance.connected : false,
            instanceId: instanceId,
            expiresIn: 0
        });
    }
});

app.post('/connect/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    
    const instance = instances.get(instanceId);
    if (!instance || (!instance.connected && !instance.connecting)) {
        connectInstance(instanceId || 'default');
        res.json({ success: true, message: `Iniciando conexão para instância ${instanceId}...` });
    } else if (instance.connecting) {
        res.json({ success: true, message: `Instância ${instanceId} já está conectando...` });
    } else {
        res.json({ success: false, message: `Instância ${instanceId} já está conectada` });
    }
});

app.post('/disconnect/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    const instance = instances.get(instanceId);
    
    if (instance && instance.sock) {
        try {
            instance.sock.logout();
            instances.delete(instanceId);
            stopQRRefresh();
            res.json({ success: true, message: `Instância ${instanceId} desconectada` });
        } catch (err) {
            res.json({ success: false, message: `Erro ao desconectar ${instanceId}: ${err.message}` });
        }
    } else {
        res.json({ success: false, message: 'Instância não encontrada' });
    }
});

app.post('/send/:instanceId', async (req, res) => {
    const { instanceId } = req.params;
    const { to, message, type = 'text' } = req.body;
    
    const instance = instances.get(instanceId);
    if (!instance || !instance.connected || !instance.sock) {
        return res.status(400).json({ error: 'Instância não conectada', instanceId: instanceId });
    }
    
    try {
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        
        if (type === 'text') {
            await instance.sock.sendMessage(jid, { text: message });
        } else if (type === 'image' && req.body.imageData) {
            // Handle image sending (base64)
            const buffer = Buffer.from(req.body.imageData, 'base64');
            await instance.sock.sendMessage(jid, { 
                image: buffer,
                caption: message || ''
            });
        }
        
        console.log(`📤 Mensagem enviada da instância ${instanceId} para ${to}`);
        res.json({ success: true, instanceId: instanceId });
    } catch (error) {
        console.error(`❌ Erro ao enviar mensagem da instância ${instanceId}:`, error);
        res.status(500).json({ error: error.message, instanceId: instanceId });
    }
});

// Groups endpoint with robust error handling  
app.get('/groups/:instanceId', async (req, res) => {
    const { instanceId } = req.params;
    
    try {
        const instance = instances.get(instanceId);
        if (!instance || !instance.connected || !instance.sock) {
            return res.status(400).json({ 
                success: false,
                error: `Instância ${instanceId} não está conectada`,
                instanceId: instanceId,
                groups: []
            });
        }
        
        console.log(`📥 Buscando grupos para instância: ${instanceId}`);
        
        // Multiple methods to get groups
        let groups = [];
        
        try {
            // Method 1: Get group metadata
            const groupIds = await instance.sock.groupFetchAllParticipating();
            console.log(`📊 Encontrados ${Object.keys(groupIds).length} grupos via groupFetchAllParticipating`);
            
            for (const [groupId, groupData] of Object.entries(groupIds)) {
                groups.push({
                    id: groupId,
                    name: groupData.subject || 'Grupo sem nome',
                    description: groupData.desc || '',
                    participants: groupData.participants ? groupData.participants.length : 0,
                    admin: groupData.participants ? 
                           groupData.participants.some(p => p.admin && p.id === instance.user?.id) : false,
                    created: groupData.creation || null
                });
            }
        } catch (error) {
            console.log(`⚠️ Método 1 falhou: ${error.message}`);
            
            try {
                // Method 2: Get chats and filter groups
                const chats = await instance.sock.getChats();
                const groupChats = chats.filter(chat => chat.id.endsWith('@g.us'));
                console.log(`📊 Encontrados ${groupChats.length} grupos via getChats`);
                
                groups = groupChats.map(chat => ({
                    id: chat.id,
                    name: chat.name || chat.subject || 'Grupo sem nome',
                    description: chat.description || '',
                    participants: chat.participantsCount || 0,
                    admin: false, // Cannot determine admin status from chat
                    created: chat.timestamp || null,
                    lastMessage: chat.lastMessage ? {
                        text: chat.lastMessage.message || '',
                        timestamp: chat.lastMessage.timestamp
                    } : null
                }));
            } catch (error2) {
                console.log(`⚠️ Método 2 falhou: ${error2.message}`);
                
                // Method 3: Simple fallback - return empty with proper structure
                groups = [];
            }
        }
        
        console.log(`✅ Retornando ${groups.length} grupos para instância ${instanceId}`);
        
        res.json({
            success: true,
            instanceId: instanceId,
            groups: groups,
            count: groups.length,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error(`❌ Erro ao buscar grupos para instância ${instanceId}:`, error);
        res.status(500).json({
            success: false,
            error: `Erro interno ao buscar grupos: ${error.message}`,
            instanceId: instanceId,
            groups: []
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    const connectedInstances = Array.from(instances.values()).filter(i => i.connected).length;
    const connectingInstances = Array.from(instances.values()).filter(i => i.connecting).length;
    
    res.json({
        status: 'running',
        instances: {
            total: instances.size,
            connected: connectedInstances,
            connecting: connectingInstances
        },
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

const PORT = process.env.PORT || 3002;
const BASE_URL = process.env.BAILEYS_URL || `http://localhost:${PORT}`;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Baileys service rodando na porta ${PORT}`);
    console.log(`📊 Health check: ${BASE_URL}/health`);
    console.log('⏳ Aguardando comandos para conectar instâncias...');
});'''
            
            server_path = f"{self.baileys_dir}/server.js"
            with open(server_path, 'w') as f:
                f.write(baileys_server)
            print("✅ server.js criado")
            
            # Install dependencies
            print("📦 Iniciando instalação das dependências...")
            print("   Isso pode levar alguns minutos na primeira vez...")
            
            try:
                # Try npm first, then yarn
                result = subprocess.run(['npm', 'install'], cwd=self.baileys_dir, 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    print("⚠️ npm falhou, tentando yarn...")
                    result = subprocess.run(['yarn', 'install'], cwd=self.baileys_dir, 
                                          capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✅ Dependências instaladas com sucesso!")
                    # Install node-fetch specifically (required for backend communication)
                    print("📦 Instalando node-fetch...")
                    fetch_result = subprocess.run(['npm', 'install', 'node-fetch@2.6.7'], 
                                                cwd=self.baileys_dir, capture_output=True, text=True)
                    if fetch_result.returncode == 0:
                        print("✅ node-fetch instalado com sucesso!")
                    else:
                        print("⚠️ Aviso: node-fetch pode não ter sido instalado corretamente")
                else:
                    print(f"❌ Erro na instalação: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout na instalação - continuando mesmo assim...")
            except FileNotFoundError:
                print("❌ npm/yarn não encontrado. Por favor instale Node.js primeiro.")
                return False
            
            # Start the service
            print("🚀 Iniciando serviço Baileys...")
            try:
                self.process = subprocess.Popen(
                    ['node', 'server.js'],
                    cwd=self.baileys_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.is_running = True
                
                # Wait a bit and check if it's still running
                time.sleep(3)
                if self.process.poll() is None:
                    print("✅ Baileys iniciado com sucesso!")
                    return True
                else:
                    stdout, stderr = self.process.communicate()
                    print(f"❌ Baileys falhou ao iniciar:")
                    print(f"stdout: {stdout}")
                    print(f"stderr: {stderr}")
                    return False
                    
            except FileNotFoundError:
                print("❌ Node.js não encontrado no sistema")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao configurar Baileys: {e}")
            return False
    
    def stop_baileys(self):
        """Stop Baileys service"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                print("✅ Baileys parado com sucesso")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("⚠️ Baileys forçadamente terminado")
            
            self.is_running = False
            self.process = None

# HTTP Handler with Baileys integration
class WhatsFlowRealHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html_response(HTML_APP)
        elif self.path == '/api/instances':
            self.handle_get_instances()
        elif self.path == '/api/stats':
            self.handle_get_stats()
        elif self.path == '/api/messages':
            self.handle_get_messages()
        elif self.path == '/api/whatsapp/status':
            # Fallback for backward compatibility - use default instance
            self.handle_whatsapp_status('default')
        elif self.path == '/api/whatsapp/qr':
            # Fallback for backward compatibility - use default instance
            self.handle_whatsapp_qr('default')
        elif self.path == '/api/contacts':
            self.handle_get_contacts()
        elif self.path == '/api/chats':
            self.handle_get_chats()
        elif self.path == '/api/flows':
            self.handle_get_flows()
        elif self.path.startswith('/api/campaigns/') and self.path.endswith('/messages'):
            campaign_id = self.path.split('/')[-2]
            self.handle_get_campaign_messages(campaign_id)
        elif self.path.startswith('/api/campaigns/'):
            campaign_id = self.path.split('/')[-1]
            self.handle_get_campaign(campaign_id)
        elif self.path == '/api/campaigns':
            self.handle_get_campaigns()
        elif self.path.startswith('/api/groups/'):
            instance_id = self.path.split('/')[-1]
            self.handle_get_groups(instance_id)
        elif self.path == '/api/webhooks/send':
            self.handle_send_webhook()
        elif self.path.startswith('/api/whatsapp/status/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_status(instance_id)
        elif self.path.startswith('/api/whatsapp/qr/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_qr(instance_id)
        elif self.path.startswith('/api/messages?'):
            self.handle_get_messages_filtered()
        elif self.path == '/api/webhooks':
            self.handle_get_webhooks()
        elif self.path == '/api/messages/scheduled':
            self.handle_get_scheduled_messages()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/api/instances':
            self.handle_create_instance()
        elif self.path.startswith('/api/instances/') and self.path.endswith('/connect'):
            instance_id = self.path.split('/')[-2]
            self.handle_connect_instance(instance_id)
        elif self.path.startswith('/api/instances/') and self.path.endswith('/disconnect'):
            instance_id = self.path.split('/')[-2]
            self.handle_disconnect_instance(instance_id)
        elif self.path == '/api/messages/receive':
            self.handle_receive_message()
        elif self.path == '/api/whatsapp/connected':
            self.handle_whatsapp_connected()
        elif self.path == '/api/whatsapp/disconnected':
            self.handle_whatsapp_disconnected()
        elif self.path == '/api/chats/import':
            self.handle_import_chats()
        elif self.path.startswith('/api/whatsapp/connect/'):
            instance_id = self.path.split('/')[-1]
            self.handle_connect_instance(instance_id)
        elif self.path.startswith('/api/whatsapp/disconnect/'):
            instance_id = self.path.split('/')[-1]
            self.handle_disconnect_instance(instance_id)
        elif self.path.startswith('/api/whatsapp/status/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_status(instance_id)
        elif self.path.startswith('/api/whatsapp/qr/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_qr(instance_id)
        elif self.path.startswith('/api/messages/send/'):
            instance_id = self.path.split('/')[-1]
            self.handle_send_message(instance_id)
        elif self.path.startswith('/api/campaigns/') and self.path.endswith('/messages'):
            campaign_id = self.path.split('/')[-2]
            self.handle_schedule_campaign_message(campaign_id)
        elif self.path == '/api/messages/schedule':
            self.handle_schedule_message()
        elif self.path == '/api/flows':
            self.handle_create_flow()
        elif self.path == '/api/campaigns':
            self.handle_create_campaign()
        elif self.path == '/api/webhooks/send':
            self.handle_send_webhook()
        else:
            self.send_error(404, "Not Found")
    
    def do_PUT(self):
        if self.path.startswith('/api/flows/'):
            flow_id = self.path.split('/')[-1]
            self.handle_update_flow(flow_id)
        elif self.path.startswith('/api/campaigns/'):
            campaign_id = self.path.split('/')[-1]
            self.handle_update_campaign(campaign_id)
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        if self.path.startswith('/api/instances/'):
            instance_id = self.path.split('/')[-1]
            self.handle_delete_instance(instance_id)
        elif self.path.startswith('/api/flows/'):
            flow_id = self.path.split('/')[-1]
            self.handle_delete_flow(flow_id)
        elif self.path.startswith('/api/campaigns/'):
            campaign_id = self.path.split('/')[-1]
            self.handle_delete_campaign(campaign_id)
        elif self.path.startswith('/api/messages/scheduled/'):
            schedule_id = self.path.split('/')[-1]
            self.handle_delete_scheduled_message(schedule_id)
        else:
            self.send_error(404, "Not Found")
    
    def send_html_response(self, html_content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def handle_get_instances(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
            instances = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(instances)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_get_stats(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contacts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            messages_count = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                "contacts_count": contacts_count,
                "conversations_count": contacts_count,
                "messages_count": messages_count
            }
            
            self.send_json_response(stats)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_get_messages(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY created_at DESC LIMIT 50")
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(messages)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_schedule_message(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
            campaign_id = data.get('campaign_id') or data.get('campaignId')
            content = data.get('content') or data.get('message', '')
            media_type = data.get('media_type') or data.get('mediaType', 'text')
            media_path = data.get('media_path')
            groups = data.get('groups', [])

            if not campaign_id:
                self.send_json_response({"error": "Dados inválidos"}, 400)
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT recurrence, send_time, weekday FROM campaigns WHERE id = ?",
                (campaign_id,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({"error": "Campanha não encontrada"}, 404)
                return
            recurrence, send_time, weekday = row
            next_run = calculate_next_run(recurrence or 'once', send_time or '00:00', weekday)

            schedule_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO scheduled_messages (id, campaign_id, content, media_type, media_path, next_run, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    schedule_id,
                    campaign_id,
                    content,
                    media_type,
                    media_path,
                    next_run,
                ),
            )

            for gid in groups:
                cursor.execute(
                    "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                    (campaign_id, gid),
                )

            conn.commit()
            conn.close()
            self.send_json_response({"success": True, "id": schedule_id})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_scheduled_messages(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT sm.id, sm.campaign_id, c.name as campaign_name, sm.content, sm.media_type, sm.media_path, sm.next_run, sm.status
                FROM scheduled_messages sm
                JOIN campaigns c ON c.id = sm.campaign_id
                ORDER BY sm.next_run ASC
                """,
            )
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(messages)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_schedule_campaign_message(self, campaign_id: str) -> None:
        """Schedule a message for a specific campaign."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
            content = data.get('content') or data.get('message', '')
            media_type = data.get('media_type') or data.get('mediaType', 'text')
            media_path = data.get('media_path')
            groups = data.get('groups')

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT recurrence, send_time, weekday FROM campaigns WHERE id = ?",
                (campaign_id,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            allowed_groups = {g[0] for g in cursor.fetchall()}
            if not allowed_groups:
                conn.close()
                self.send_json_response({'error': 'Nenhum grupo associado à campanha'}, 400)
                return

            if groups:
                if not set(groups).issubset(allowed_groups):
                    conn.close()
                    self.send_json_response({'error': 'Grupos inválidos para esta campanha'}, 400)
                    return

            recurrence, send_time, weekday = row
            next_run = calculate_next_run(recurrence or 'once', send_time or '00:00', weekday)

            schedule_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO scheduled_messages (id, campaign_id, content, media_type, media_path, next_run, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (schedule_id, campaign_id, content, media_type, media_path, next_run),
            )

            conn.commit()
            conn.close()
            self.send_json_response({'success': True, 'id': schedule_id}, 201)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_get_campaign_messages(self, campaign_id: str) -> None:
        """List scheduled messages for a campaign."""
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM campaigns WHERE id = ?", (campaign_id,))
            if not cursor.fetchone():
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            groups = [g[0] for g in cursor.fetchall()]
            if not groups:
                conn.close()
                self.send_json_response({'error': 'Nenhum grupo associado à campanha'}, 400)
                return

            cursor.execute(
                """
                SELECT id, content, media_type, media_path, next_run, status
                FROM scheduled_messages
                WHERE campaign_id = ?
                ORDER BY next_run ASC
                """,
                (campaign_id,),
            )
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response({'campaign_id': campaign_id, 'groups': groups, 'messages': messages})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_delete_scheduled_message(self, schedule_id: str):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scheduled_messages WHERE id = ?", (schedule_id,))
            conn.commit()
            conn.close()
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_create_instance(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response({"error": "No data provided"}, 400)
                return
                
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'name' not in data or not data['name'].strip():
                self.send_json_response({"error": "Name is required"}, 400)
                return
            
            instance_id = str(uuid.uuid4())
            created_at = datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO instances (id, name, created_at)
                VALUES (?, ?, ?)
            """, (instance_id, data['name'].strip(), created_at))
            conn.commit()
            conn.close()
            
            result = {
                "id": instance_id,
                "name": data['name'].strip(),
                "connected": 0,
                "contacts_count": 0,
                "messages_today": 0,
                "created_at": created_at
            }
            
            self.send_json_response(result, 201)
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_connect_instance(self, instance_id):
        try:
            # Start Baileys connection
            try:
                import requests
                response = requests.post(f'{BAILEYS_URL}/connect', timeout=5)
                
                if response.status_code == 200:
                    self.send_json_response({"success": True, "message": "Conexão iniciada"})
                else:
                    self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
            except ImportError:
                # Fallback usando urllib se requests não estiver disponível
                import urllib.request
                import urllib.error

                try:
                    data = json.dumps({}).encode('utf-8')
                    req = urllib.request.Request(
                        'http://127.0.0.1:3002/connect',
                        data=data,
                        headers={'Content-Type': 'application/json'},
                    )

                    req.get_method = lambda: 'POST'

                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            self.send_json_response({"success": True, "message": "Conexão iniciada"})
                        else:
                            self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
                except urllib.error.URLError as e:
                    self.send_json_response({"error": f"Serviço WhatsApp indisponível: {str(e)}"}, 500)
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_whatsapp_status(self):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/status', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"connected": False, "connecting": False})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/status', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"connected": False, "connecting": False})
                except:
                    self.send_json_response({"connected": False, "connecting": False})
                
        except Exception as e:
            self.send_json_response({"connected": False, "connecting": False, "error": str(e)})
    
    def handle_whatsapp_qr(self):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/qr', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"qr": None, "connected": False})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/qr', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"qr": None, "connected": False})
                except:
                    self.send_json_response({"qr": None, "connected": False})
                
        except Exception as e:
            self.send_json_response({"qr": None, "connected": False, "error": str(e)})
    
    def handle_whatsapp_disconnected(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            reason = data.get('reason', 'unknown')
            
            # Update instance connection status
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE instances SET connected = 0, user_name = NULL, user_id = NULL
                WHERE id = ?
            """, (instance_id,))
            
            conn.commit()
            conn.close()
            
            print(f"❌ WhatsApp desconectado na instância {instance_id} - Razão: {reason}")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar desconexão: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_import_chats(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            chats = data.get('chats', [])
            user = data.get('user', {})
            batch_number = data.get('batchNumber', 1)
            total_batches = data.get('totalBatches', 1)
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Update instance with user info on first batch
            if batch_number == 1:
                cursor.execute("""
                    UPDATE instances SET connected = 1, user_name = ?, user_id = ? 
                    WHERE id = ?
                """, (user.get('name', ''), user.get('id', ''), instance_id))
                print(f"👤 Usuário atualizado: {user.get('name', '')} ({user.get('phone', '')})")
            
            # Import contacts and chats from this batch
            imported_contacts = 0
            imported_chats = 0
            
            for chat in chats:
                if chat.get('id') and not chat['id'].endswith('@g.us'):  # Skip groups for now
                    phone = chat['id'].replace('@s.whatsapp.net', '').replace('@c.us', '')
                    contact_name = chat.get('name') or f"Contato {phone[-4:]}"
                    
                    # Check if contact exists
                    cursor.execute("SELECT id FROM contacts WHERE phone = ? AND instance_id = ?", (phone, instance_id))
                    if not cursor.fetchone():
                        contact_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO contacts (id, name, phone, instance_id, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (contact_id, contact_name, phone, instance_id, datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
                        imported_contacts += 1
                    
                    # Create/update chat entry
                    last_message = None
                    last_message_time = None
                    unread_count = chat.get('unreadCount', 0)
                    
                    # Try to get last message from chat
                    if chat.get('messages') and len(chat['messages']) > 0:
                        last_msg = chat['messages'][-1]
                        if last_msg.get('message'):
                            last_message = last_msg['message'].get('conversation') or 'Mídia'
                            last_message_time = datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()
                    
                    # Insert or update chat
                    cursor.execute("SELECT id FROM chats WHERE contact_phone = ? AND instance_id = ?", (phone, instance_id))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE chats SET contact_name = ?, last_message = ?, last_message_time = ?, unread_count = ?
                            WHERE contact_phone = ? AND instance_id = ?
                        """, (contact_name, last_message, last_message_time, unread_count, phone, instance_id))
                    else:
                        chat_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO chats (id, contact_phone, contact_name, instance_id, last_message, last_message_time, unread_count, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (chat_id, phone, contact_name, instance_id, last_message, last_message_time, unread_count, datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
                        imported_chats += 1
            
            conn.commit()
            conn.close()
            
            print(f"📦 Lote {batch_number}/{total_batches} processado: {imported_contacts} contatos, {imported_chats} chats - Instância: {instance_id}")
            
            # If this is the last batch, log completion
            if batch_number == total_batches:
                print(f"✅ Importação completa para instância {instance_id}!")
            
            self.send_json_response({
                "success": True, 
                "imported_contacts": imported_contacts,
                "imported_chats": imported_chats,
                "batch": batch_number,
                "total_batches": total_batches
            })
            
        except Exception as e:
            print(f"❌ Erro ao importar chats: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_connect_instance(self, instance_id):
        try:
            # Start Baileys connection for specific instance
            try:
                import requests
                response = requests.post(f'{BAILEYS_URL}/connect/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    self.send_json_response({"success": True, "message": f"Conexão da instância {instance_id} iniciada"})
                else:
                    self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
            except ImportError:
                # Fallback usando urllib se requests não estiver disponível
                import urllib.request
                import urllib.error

                try:
                    data = json.dumps({}).encode('utf-8')
                    req = urllib.request.Request(
                        f'http://127.0.0.1:3002/connect/{instance_id}',
                        data=data,
                        headers={'Content-Type': 'application/json'},
                    )

                    req.get_method = lambda: 'POST'

                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            self.send_json_response({"success": True, "message": f"Conexão da instância {instance_id} iniciada"})
                        else:
                            self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
                except urllib.error.URLError as e:
                    self.send_json_response({"error": f"Serviço WhatsApp indisponível: {str(e)}"}, 500)
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_disconnect_instance(self, instance_id):
        try:
            try:
                import requests
                response = requests.post(f'{BAILEYS_URL}/disconnect/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    # Update database
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE instances SET connected = 0 WHERE id = ?", (instance_id,))
                    conn.commit()
                    conn.close()
                    
                    self.send_json_response({"success": True, "message": f"Instância {instance_id} desconectada"})
                else:
                    self.send_json_response({"error": "Erro ao desconectar"}, 500)
            except ImportError:
                # Fallback usando urllib
                import urllib.request
                data = json.dumps({}).encode('utf-8')
                req = urllib.request.Request(
                    f'http://127.0.0.1:3002/disconnect/{instance_id}',
                    data=data,
                    headers={'Content-Type': 'application/json'},
                )

                req.get_method = lambda: 'POST'
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE instances SET connected = 0 WHERE id = ?", (instance_id,))
                        conn.commit()
                        conn.close()
                        self.send_json_response({"success": True, "message": f"Instância {instance_id} desconectada"})
                    else:
                        self.send_json_response({"error": "Erro ao desconectar"}, 500)
                        
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_whatsapp_status(self, instance_id):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/status/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/status/{instance_id}', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
                except:
                    self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
                
        except Exception as e:
            self.send_json_response({"connected": False, "connecting": False, "error": str(e), "instanceId": instance_id})

    def handle_whatsapp_qr(self, instance_id):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/qr/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/qr/{instance_id}', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
                except:
                    self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
                
        except Exception as e:
            self.send_json_response({"qr": None, "connected": False, "error": str(e), "instanceId": instance_id})

    def handle_get_groups(self, instance_id):
        try:
            try:
                import requests
                try:
                    response = requests.get(f'{BAILEYS_URL}/groups/{instance_id}', timeout=5)
                except requests.exceptions.RequestException:
                    self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
                    return

                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"error": "Erro ao obter grupos"}, response.status_code)
            except ImportError:
                import urllib.request
                import urllib.error
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/groups/{instance_id}', timeout=5) as resp:
                        if resp.status == 200:
                            data = json.loads(resp.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"error": "Erro ao obter grupos"}, resp.status)
                except urllib.error.URLError:
                    self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_send_message(self, instance_id):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            to = data.get('to', '')
            message = data.get('message', '')
            message_type = data.get('type', 'text')
            
            try:
                import requests
                try:
                    response = requests.post(
                        f'http://127.0.0.1:3002/send/{instance_id}',
                        json=data, timeout=10
                    )
                except requests.exceptions.RequestException as e:
                    self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
                    return
                
                if response.status_code == 200:
                    # Save message to database
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    
                    message_id = str(uuid.uuid4())
                    phone = to.replace('@s.whatsapp.net', '').replace('@c.us', '')
                    
                    cursor.execute("""
                        INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (message_id, f"Para {phone[-4:]}", phone, message, 'outgoing', instance_id, 
                          datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
                    
                    conn.commit()
                    conn.close()
                    
                    self.send_json_response({"success": True, "instanceId": instance_id})
                else:
                    self.send_json_response({"error": "Erro ao enviar mensagem"}, 500)
            except ImportError:
                # Fallback usando urllib
                import urllib.request
                req_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(
                    f'http://127.0.0.1:3002/send/{instance_id}',
                    data=req_data,
                    headers={'Content-Type': 'application/json'},
                )

                req.get_method = lambda: 'POST'
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status == 200:
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()

                            message_id = str(uuid.uuid4())
                            phone = to.replace('@s.whatsapp.net', '').replace('@c.us', '')

                            cursor.execute("""
                                INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (message_id, f"Para {phone[-4:]}", phone, message, 'outgoing', instance_id,
                                  datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))

                            conn.commit()
                            conn.close()

                            self.send_json_response({"success": True, "instanceId": instance_id})
                        else:
                            self.send_json_response({"error": "Erro ao enviar mensagem"}, 500)
                except Exception:
                    self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
                    return
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_whatsapp_connected(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            user = data.get('user', {})
            
            # Update instance connection status
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE instances SET connected = 1, user_name = ?, user_id = ?
                WHERE id = ?
            """, (user.get('name', ''), user.get('id', ''), instance_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ WhatsApp conectado na instância {instance_id}: {user.get('name', user.get('id', 'Unknown'))}")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar conexão: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_receive_message(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract message info
            instance_id = data.get('instanceId', 'default')
            from_jid = data.get('from', '')
            message = data.get('message', '')
            timestamp = data.get('timestamp', datetime.now(BR_TZ).astimezone(timezone.utc).isoformat())
            message_id = data.get('messageId', str(uuid.uuid4()))
            message_type = data.get('messageType', 'text')
            
            # Extract real contact name from WhatsApp data
            contact_name = data.get('pushName', data.get('contactName', ''))
            
            # Clean phone number
            phone = from_jid.replace('@s.whatsapp.net', '').replace('@c.us', '')
            
            # If no name provided, use formatted phone number
            if not contact_name or contact_name == phone:
                formatted_phone = self.format_phone_number(phone)
                contact_name = formatted_phone
            
            # Save message and create/update contact
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Create or update contact with real name
            contact_id = f"{phone}_{instance_id}"
            cursor.execute("""
                INSERT OR REPLACE INTO contacts (id, name, phone, instance_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (contact_id, contact_name, phone, instance_id, timestamp))
            
            # Save message
            msg_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, message_type, whatsapp_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, contact_name, phone, message, 'incoming', instance_id, message_type, message_id, timestamp))
            
            # Create or update chat conversation
            chat_id = f"{phone}_{instance_id}"
            cursor.execute("""
                INSERT OR REPLACE INTO chats (id, contact_phone, contact_name, instance_id, last_message, last_message_time, unread_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT unread_count FROM chats WHERE id = ?), 0) + 1, ?)
            """, (chat_id, phone, contact_name, instance_id, message[:100], timestamp, chat_id, timestamp))
            
            conn.commit()
            conn.close()
            
            print(f"📥 Mensagem recebida na instância {instance_id}")
            print(f"👤 Contato: {contact_name} ({phone})")
            print(f"💬 Mensagem: {message[:50]}...")
            
            # Broadcast via WebSocket if available
            if WEBSOCKETS_AVAILABLE and websocket_clients:
                asyncio.create_task(broadcast_message({
                    'type': 'new_message',
                    'message': {
                        'id': msg_id,
                        'contact_name': contact_name,
                        'phone': phone,
                        'message': message,
                        'direction': 'incoming',
                        'instance_id': instance_id,
                        'created_at': timestamp
                    }
                }))
            
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def format_phone_number(self, phone):
        """Format phone number for Brazilian display"""
        cleaned = phone.replace('+', '').replace('-', '').replace(' ', '')
        
        if len(cleaned) == 13 and cleaned.startswith('55'):
            # Brazilian format: +55 (11) 99999-9999
            return f"+55 ({cleaned[2:4]}) {cleaned[4:9]}-{cleaned[9:]}"
        elif len(cleaned) == 11:
            # Local format: (11) 99999-9999
            return f"({cleaned[0:2]}) {cleaned[2:7]}-{cleaned[7:]}"
        else:
            # Return as is if format not recognized
            return phone
    
    def handle_get_contacts(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            contacts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(contacts)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_get_chats(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get chats with latest message info
            cursor.execute("""
                SELECT DISTINCT
                    c.phone as contact_phone,
                    c.name as contact_name, 
                    c.instance_id,
                    (SELECT message FROM messages m WHERE m.phone = c.phone ORDER BY m.created_at DESC LIMIT 1) as last_message,
                    (SELECT created_at FROM messages m WHERE m.phone = c.phone ORDER BY m.created_at DESC LIMIT 1) as last_message_time,
                    (SELECT COUNT(*) FROM messages m WHERE m.phone = c.phone AND m.direction = 'incoming') as unread_count
                FROM contacts c
                WHERE EXISTS (SELECT 1 FROM messages m WHERE m.phone = c.phone)
                ORDER BY last_message_time DESC
            """)
            
            chats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(chats)
            
        except Exception as e:
            print(f"❌ Erro ao buscar chats: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_messages_filtered(self):
        try:
            # Parse query parameters
            query_components = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(query_components.query)
            
            phone = query_params.get('phone', [None])[0]
            instance_id = query_params.get('instance_id', [None])[0]
            
            if not phone:
                self.send_json_response({"error": "Phone parameter required"}, 400)
                return
            
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if instance_id:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE phone = ? AND instance_id = ? 
                    ORDER BY created_at ASC
                """, (phone, instance_id))
            else:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE phone = ? 
                    ORDER BY created_at ASC
                """, (phone,))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self.send_json_response(messages)
            
        except Exception as e:
            print(f"❌ Erro ao buscar mensagens filtradas: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_send_webhook(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            webhook_url = data.get('url', '')
            webhook_data = data.get('data', {})
            
            if not webhook_url:
                self.send_json_response({"error": "URL do webhook é obrigatória"}, 400)
                return
            
            # Send webhook using urllib (no external dependencies)
            import urllib.request
            import urllib.error
            
            try:
                payload = json.dumps(webhook_data).encode('utf-8')
                req = urllib.request.Request(
                    webhook_url, 
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'WhatsFlow-Real/1.0'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        print(f"✅ Webhook enviado para: {webhook_url}")
                        self.send_json_response({"success": True, "message": "Webhook enviado com sucesso"})
                    else:
                        print(f"⚠️ Webhook retornou status: {response.status}")
                        self.send_json_response({"success": True, "message": f"Webhook enviado (status: {response.status})"})
                        
            except urllib.error.URLError as e:
                print(f"❌ Erro ao enviar webhook: {e}")
                self.send_json_response({"error": f"Erro ao enviar webhook: {str(e)}"}, 500)
                
        except Exception as e:
            print(f"❌ Erro no processamento do webhook: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_webhooks(self):
        try:
            # Return a list of configured webhooks
            # For now, return an empty list as this is a placeholder implementation
            webhooks = []
            self.send_json_response(webhooks)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_delete_instance(self, instance_id):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                self.send_json_response({"error": "Instance not found"}, 404)
                return
            
            conn.commit()
            conn.close()
            
            self.send_json_response({"message": "Instance deleted successfully"})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    # Flow Management Functions
    def handle_get_flows(self):
        """Get all flows"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM flows 
                ORDER BY created_at DESC
            """)
            
            flows = []
            for row in cursor.fetchall():
                flows.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'nodes': json.loads(row[3]) if row[3] else [],
                    'edges': json.loads(row[4]) if row[4] else [],
                    'active': bool(row[5]),
                    'instance_id': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            
            conn.close()
            self.send_json_response(flows)
            
        except Exception as e:
            print(f"❌ Erro ao obter fluxos: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_create_flow(self):
        """Create new flow"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            flow_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO flows (id, name, description, nodes, edges, active, instance_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (flow_id, data['name'], data.get('description', ''), 
                  json.dumps(data.get('nodes', [])), json.dumps(data.get('edges', [])),
                  data.get('active', False), data.get('instance_id'),
                  datetime.now(BR_TZ).astimezone(timezone.utc).isoformat(), datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Fluxo '{data['name']}' criado com ID: {flow_id}")
            self.send_json_response({
                'success': True,
                'flow_id': flow_id,
                'message': f'Fluxo "{data["name"]}" criado com sucesso'
            })
            
        except Exception as e:
            print(f"❌ Erro ao criar fluxo: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_update_flow(self, flow_id):
        """Update flow"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Update only the provided fields
            update_fields = []
            values = []
            
            if 'name' in data:
                update_fields.append('name = ?')
                values.append(data['name'])
                
            if 'description' in data:
                update_fields.append('description = ?')
                values.append(data['description'])
                
            if 'nodes' in data:
                update_fields.append('nodes = ?')
                values.append(json.dumps(data['nodes']))
                
            if 'edges' in data:
                update_fields.append('edges = ?')
                values.append(json.dumps(data['edges']))
                
            if 'active' in data:
                update_fields.append('active = ?')
                values.append(data['active'])
                
            if 'instance_id' in data:
                update_fields.append('instance_id = ?')
                values.append(data['instance_id'])
            
            update_fields.append('updated_at = ?')
            values.append(datetime.now(BR_TZ).astimezone(timezone.utc).isoformat())
            
            values.append(flow_id)
            
            cursor.execute(f"""
                UPDATE flows 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"✅ Fluxo {flow_id} atualizado")
                self.send_json_response({'success': True, 'message': 'Fluxo atualizado com sucesso'})
            else:
                conn.close()
                self.send_json_response({'error': 'Fluxo não encontrado'}, 404)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar fluxo: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_delete_flow(self, flow_id):
        """Delete flow"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM flows WHERE id = ?", (flow_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"✅ Fluxo {flow_id} excluído")
                self.send_json_response({'success': True, 'message': 'Fluxo excluído com sucesso'})
            else:
                conn.close()
                self.send_json_response({'error': 'Fluxo não encontrado'}, 404)
            
        except Exception as e:
            print(f"❌ Erro ao excluir fluxo: {e}")
            self.send_json_response({"error": str(e)}, 500)

    # Campaign Management Functions
    def handle_get_campaigns(self):
        """Get all campaigns"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, recurrence, send_time, weekday FROM campaigns")
            campaigns = []
            for row in cursor.fetchall():
                campaign_id = row[0]
                cursor.execute(
                    "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                    (campaign_id,),
                )
                groups = [g[0] for g in cursor.fetchall()]
                campaigns.append({
                    'id': campaign_id,
                    'name': row[1],
                    'description': row[2],
                    'recurrence': row[3],
                    'send_time': row[4],
                    'weekday': row[5],
                    'groups': groups,
                })
            conn.close()
            self.send_json_response(campaigns)

        except Exception as e:
            print(f"❌ Erro ao obter campanhas: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_get_campaign(self, campaign_id):
        """Get a single campaign"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("SELECT id, name, description, recurrence, send_time, weekday FROM campaigns WHERE id = ?", (campaign_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            groups = [g[0] for g in cursor.fetchall()]

            campaign = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'recurrence': row[3],
                'send_time': row[4],
                'weekday': row[5],
                'groups': groups,
            }

            conn.close()
            self.send_json_response(campaign)

        except Exception as e:
            print(f"❌ Erro ao obter campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_create_campaign(self):
        """Create new campaign"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            campaign_id = str(uuid.uuid4())

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            groups = data.get('groups', [])
            if not isinstance(groups, list) or not groups:
                conn.close()
                self.send_json_response({'error': 'Grupos inválidos ou ausentes'}, 400)
                return

            cursor.execute(
                """
                INSERT INTO campaigns (id, name, description, recurrence, send_time, weekday)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    data['name'],
                    data.get('description'),
                    data.get('recurrence'),
                    data.get('send_time'),
                    data.get('weekday')
                ),
            )

            for group_id in groups:
                cursor.execute(
                    "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                    (campaign_id, group_id),
                )

            conn.commit()
            conn.close()

            self.send_json_response({'success': True, 'campaign_id': campaign_id})

        except Exception as e:
            print(f"❌ Erro ao criar campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_update_campaign(self, campaign_id):
        """Update campaign"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            update_fields = []
            values = []

            if 'name' in data:
                update_fields.append('name = ?')
                values.append(data['name'])

            if 'description' in data:
                update_fields.append('description = ?')
                values.append(data['description'])

            if 'recurrence' in data:
                update_fields.append('recurrence = ?')
                values.append(data['recurrence'])

            if 'send_time' in data:
                update_fields.append('send_time = ?')
                values.append(data['send_time'])

            if 'weekday' in data:
                update_fields.append('weekday = ?')
                values.append(data['weekday'])

            values.append(campaign_id)
            cursor.execute(
                f"UPDATE campaigns SET {', '.join(update_fields)} WHERE id = ?",
                values,
            )

            if cursor.rowcount == 0:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            if 'groups' in data:
                groups = data['groups']
                if not isinstance(groups, list) or not groups:
                    conn.close()
                    self.send_json_response({'error': 'Grupos inválidos ou ausentes'}, 400)
                    return
                cursor.execute("DELETE FROM campaign_groups WHERE campaign_id = ?", (campaign_id,))
                for group_id in groups:
                    cursor.execute(
                        "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                        (campaign_id, group_id),
                    )

            conn.commit()
            conn.close()

            self.send_json_response({'success': True})

        except Exception as e:
            print(f"❌ Erro ao atualizar campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_delete_campaign(self, campaign_id):
        """Delete campaign"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM campaign_groups WHERE campaign_id = ?", (campaign_id,))
            cursor.execute("DELETE FROM scheduled_messages WHERE campaign_id = ?", (campaign_id,))
            cursor.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                self.send_json_response({'success': True})
            else:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)

        except Exception as e:
            print(f"❌ Erro ao excluir campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_send_webhook(self):
        """Send webhook"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            import urllib.request
            
            webhook_data = json.dumps(data['data']).encode()
            req = urllib.request.Request(
                data['url'],
                data=webhook_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                self.send_json_response({'success': True, 'message': 'Webhook enviado com sucesso'})
                
        except Exception as e:
            print(f"❌ Erro ao enviar webhook: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    print("🚀 WhatsFlow Professional - Sistema Avançado")
    print("=" * 50)
    print("✅ Python backend com WebSocket")
    print("✅ Node.js + Baileys para WhatsApp real")
    print("✅ Interface profissional moderna")
    print("✅ Tempo real + Design refinado")
    print()
    
    # Check Node.js
    if not check_node_installed():
        print("❌ Node.js não encontrado!")
        print("📦 Para instalar Node.js:")
        print("   Ubuntu: sudo apt install nodejs npm")
        print("   macOS:  brew install node")
        print()
        print("🔧 Continuar mesmo assim? (s/n)")
        if input().lower() != 's':
            return
    else:
        print("✅ Node.js encontrado")
    
    # Initialize database
    print("📁 Inicializando banco de dados...")
    init_db()
    add_sample_data()
    
    # Start WebSocket server
    print("🔌 Iniciando servidor WebSocket...")
    websocket_thread = start_websocket_server()
    
    # Start Baileys service
    print("📱 Iniciando serviço WhatsApp (Baileys)...")
    baileys_manager = BaileysManager()
    
    def signal_handler(sig, frame):
        print("\n🛑 Parando serviços...")
        baileys_manager.stop_baileys()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start Baileys in background
    baileys_thread = threading.Thread(target=baileys_manager.start_baileys)
    baileys_thread.daemon = True
    baileys_thread.start()
    
    # Start HTTP server in background thread
    server = HTTPServer(('0.0.0.0', PORT), WhatsFlowRealHandler)
    print(f"✅ Servidor rodando na porta {PORT}")
    print("🔗 Pronto para conectar WhatsApp REAL!")
    print(f"🌐 Acesse: http://localhost:{PORT}")
    print("🎉 Sistema profissional pronto para uso!")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Launch campaign scheduler task after server starts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(scheduled_message_scheduler())

    print("✅ WhatsFlow Professional configurado!")
    print(f"🌐 Interface: http://localhost:{PORT}")
    print(f"🔌 WebSocket: ws://localhost:{WEBSOCKET_PORT}")
    print(f"📱 WhatsApp Service: http://localhost:{BAILEYS_PORT}")
    print("🚀 Servidor iniciando...")
    print("   Para parar: Ctrl+C")
    print()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n👋 WhatsFlow Professional finalizado!")
        baileys_manager.stop_baileys()
        server.shutdown()

if __name__ == "__main__":
    main()