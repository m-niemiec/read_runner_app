import sqlite3
import json

conn = sqlite3.connect('read_runner.db')
c = conn.cursor()

# Create base table with example text.
c.execute('CREATE TABLE texts (text_id INTEGER PRIMARY KEY, text_position int, text_progress int, text_type text, '
          'text_title text, text_author text, text_body text)')
c.execute('INSERT INTO texts VALUES (2, 0, 0, "Test Type2","Test Author2", "HP", "My dear Professor, surely a sensible '
          'person like yourself can call him by his name? All this “You-Know-Who” nonsense – for eleven years I have '
          'been trying to persuade people to call him by his proper name: Voldemort.")')

# Create preferences table with default settings.
c.execute('CREATE TABLE preferences (data json)')

preferences = {
    'reading_speed': '120',
    'word_brightness': 'bright',
    'word_size': 'medium'
}

c.execute('INSERT INTO preferences VALUES (?)', [json.dumps(preferences)])

conn.commit()
conn.close()
