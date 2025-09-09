#!/usr/bin/env python3
"""
Database Migration Script for WhatsFlow Real
Migrates from old single-instance schema to new multi-instance schema
"""

import sqlite3
import sys
from datetime import datetime

def migrate_database():
    try:
        print("🔄 Iniciando migração do banco de dados...")
        conn = sqlite3.connect('/app/whatsflow.db')
        cursor = conn.cursor()
        
        # Backup current data counts
        cursor.execute("SELECT COUNT(*) FROM contacts")
        contacts_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM messages") 
        messages_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM instances")
        instances_count = cursor.fetchone()[0]
        
        print(f"📊 Dados existentes: {contacts_count} contatos, {messages_count} mensagens, {instances_count} instâncias")
        
        # 1. MIGRATE CONTACTS TABLE
        print("\n📋 Migrando tabela CONTACTS...")
        
        # Check if instance_id column exists
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'instance_id' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN instance_id TEXT DEFAULT 'default'")
            print("✅ Coluna instance_id adicionada à tabela contacts")
        
        if 'avatar_url' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN avatar_url TEXT")
            print("✅ Coluna avatar_url adicionada à tabela contacts")
            
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN created_at TEXT")
            # Update existing records with current timestamp
            current_time = datetime.now().isoformat()
            cursor.execute("UPDATE contacts SET created_at = ? WHERE created_at IS NULL", (current_time,))
            print("✅ Coluna created_at adicionada à tabela contacts")
        
        # 2. MIGRATE MESSAGES TABLE  
        print("\n💬 Migrando tabela MESSAGES...")
        
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'instance_id' not in columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN instance_id TEXT DEFAULT 'default'")
            print("✅ Coluna instance_id adicionada à tabela messages")
            
        if 'message_type' not in columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN message_type TEXT DEFAULT 'text'")
            print("✅ Coluna message_type adicionada à tabela messages")
            
        if 'whatsapp_id' not in columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN whatsapp_id TEXT")
            print("✅ Coluna whatsapp_id adicionada à tabela messages")
            
        if 'created_at' not in columns:
            # Check if we have timestamp column to migrate from
            if 'timestamp' in columns:
                cursor.execute("ALTER TABLE messages ADD COLUMN created_at TEXT")
                # Copy timestamp data to created_at
                cursor.execute("UPDATE messages SET created_at = timestamp WHERE created_at IS NULL")
                print("✅ Coluna created_at adicionada e dados migrados de timestamp")
            else:
                cursor.execute("ALTER TABLE messages ADD COLUMN created_at TEXT")
                current_time = datetime.now().isoformat()
                cursor.execute("UPDATE messages SET created_at = ? WHERE created_at IS NULL", (current_time,))
                print("✅ Coluna created_at adicionada à tabela messages")
        
        # 3. MIGRATE INSTANCES TABLE
        print("\n🔗 Migrando tabela INSTANCES...")
        
        cursor.execute("PRAGMA table_info(instances)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_name' not in columns:
            cursor.execute("ALTER TABLE instances ADD COLUMN user_name TEXT")
            print("✅ Coluna user_name adicionada à tabela instances")
            
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE instances ADD COLUMN user_id TEXT")
            print("✅ Coluna user_id adicionada à tabela instances")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        print("\n🔍 Verificando migração...")
        
        # Check final schema
        for table in ['contacts', 'messages', 'instances']:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 {table.upper()}: {', '.join(columns)}")
        
        # Verify data integrity
        cursor.execute("SELECT COUNT(*) FROM contacts")
        new_contacts_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM messages")
        new_messages_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM instances")
        new_instances_count = cursor.fetchone()[0]
        
        print(f"\n📊 Dados após migração: {new_contacts_count} contatos, {new_messages_count} mensagens, {new_instances_count} instâncias")
        
        if (contacts_count == new_contacts_count and 
            messages_count == new_messages_count and 
            instances_count == new_instances_count):
            print("✅ Migração concluída com sucesso! Nenhum dado foi perdido.")
        else:
            print("⚠️ Alerta: Contagem de dados alterada durante migração")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)