#!/usr/bin/env python3
"""
Correção final do schema - Remove coluna timestamp duplicada
"""

import sqlite3
import os
from datetime import datetime

def fix_contacts_schema():
    print("🔧 CORREÇÃO FINAL DO SCHEMA")
    
    # Backup
    backup_name = f"whatsflow-backup-final-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
    os.system(f"cp whatsflow.db {backup_name}")
    print(f"✅ Backup criado: {backup_name}")
    
    conn = sqlite3.connect('whatsflow.db')
    cursor = conn.cursor()
    
    try:
        print("1. Verificando schema atual...")
        cursor.execute("PRAGMA table_info(contacts);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colunas atuais: {columns}")
        
        if 'timestamp' in columns and 'created_at' in columns:
            print("2. Ambas colunas existem - removendo timestamp...")
            
            # Create new table without timestamp
            cursor.execute("""
                CREATE TABLE contacts_new (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    instance_id TEXT DEFAULT 'default',
                    avatar_url TEXT,
                    created_at TEXT
                )
            """)
            
            # Copy data, using timestamp as created_at if created_at is null
            cursor.execute("""
                INSERT INTO contacts_new (id, name, phone, instance_id, avatar_url, created_at)
                SELECT id, name, phone, instance_id, avatar_url, 
                       COALESCE(created_at, timestamp, ?) as created_at
                FROM contacts
            """, (datetime.now().isoformat(),))
            
            # Drop old table
            cursor.execute("DROP TABLE contacts")
            
            # Rename new table
            cursor.execute("ALTER TABLE contacts_new RENAME TO contacts")
            
            print("✅ Coluna timestamp removida com sucesso!")
            
        elif 'timestamp' in columns and 'created_at' not in columns:
            print("2. Apenas timestamp existe - renomeando para created_at...")
            cursor.execute("ALTER TABLE contacts RENAME COLUMN timestamp TO created_at")
            print("✅ Coluna timestamp renomeada para created_at!")
            
        else:
            print("2. Schema já está correto!")
        
        # Verificar resultado
        cursor.execute("PRAGMA table_info(contacts);")
        final_columns = [col[1] for col in cursor.fetchall()]
        print(f"✅ Colunas finais: {final_columns}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def fix_messages_schema():
    print("\n3. Verificando schema da tabela messages...")
    
    conn = sqlite3.connect('whatsflow.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(messages);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colunas messages: {columns}")
        
        if 'timestamp' in columns and 'created_at' in columns:
            print("4. Messages também tem duplicação - corrigindo...")
            
            cursor.execute("""
                CREATE TABLE messages_new (
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
                INSERT INTO messages_new (id, contact_name, phone, message, direction, instance_id, message_type, whatsapp_id, created_at)
                SELECT id, contact_name, phone, message, direction, instance_id, message_type, whatsapp_id,
                       COALESCE(created_at, timestamp, ?) as created_at
                FROM messages
            """, (datetime.now().isoformat(),))
            
            cursor.execute("DROP TABLE messages")
            cursor.execute("ALTER TABLE messages_new RENAME TO messages")
            
            print("✅ Messages schema corrigido!")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erro no messages: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_contacts_schema()
    if success:
        fix_messages_schema()
        print("\n🎉 SCHEMA TOTALMENTE CORRIGIDO!")
        print("Reinicie o servidor WhatsFlow agora!")
    else:
        print("\n❌ Falha na correção!")