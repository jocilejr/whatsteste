#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('/app/whatsflow.db')
cursor = conn.cursor()

print("=== DATABASE SCHEMA ANALYSIS ===")

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables found: {[t[0] for t in tables]}")

# Check contacts table structure
try:
    cursor.execute("PRAGMA table_info(contacts);")
    contacts_columns = cursor.fetchall()
    print(f"\nCONTACTS TABLE COLUMNS:")
    for col in contacts_columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"Error checking contacts table: {e}")

# Check messages table structure
try:
    cursor.execute("PRAGMA table_info(messages);")
    messages_columns = cursor.fetchall()
    print(f"\nMESSAGES TABLE COLUMNS:")
    for col in messages_columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"Error checking messages table: {e}")

# Check instances table structure
try:
    cursor.execute("PRAGMA table_info(instances);")
    instances_columns = cursor.fetchall()
    print(f"\nINSTANCES TABLE COLUMNS:")
    for col in instances_columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"Error checking instances table: {e}")

conn.close()