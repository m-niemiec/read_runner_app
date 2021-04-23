import sqlite3

conn = sqlite3.connect('read_runner.db')
c = conn.cursor()

c.execute('''CREATE TABLE texts (text_id int, text_type text, text_title text, text_author text, text_body text)''')
c.execute("INSERT INTO texts VALUES (1,'Test Type','Test Author', 'Test Title', 'This is text body')")
c.execute("INSERT INTO texts VALUES (2,'Test Type2','Test Author2', 'HP', 'My dear Professor, surely a sensible "
          "person like yourself can call him by his name? All this “You-Know-Who” nonsense – for eleven years I have "
          "been trying to persuade people to call him by his proper name: Voldemort.')")

conn.commit()
conn.close()
