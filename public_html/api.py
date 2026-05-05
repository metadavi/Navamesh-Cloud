from flask import Flask, jsonify
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('/var/www/html/nextg-ag.org/.env')

app = Flask(__name__)

PG_DSN = os.getenv("PG_DSN", "")

@app.route('/api/nodes')
def get_nodes():
    from flask import request
    farm = request.args.get('farm', None)
    try:
        conn = psycopg2.connect(PG_DSN)
        cur = conn.cursor()
        if farm == 'farm1':
            location_filter = "AND metadata->>'location' = 'FAU Garden'"
        elif farm == 'farm2':
            location_filter = "AND metadata->>'location' = 'FAU Garden 2'"
        else:
            location_filter = ""
        cur.execute(f"""
            SELECT node_id, lat, lon,
                   metadata->>'soil_percent' as soil,
                   metadata->>'battery_level' as battery,
                   last_seen
            FROM mesh_nodes
            WHERE lat IS NOT NULL AND lon IS NOT NULL
            {location_filter}
            ORDER BY last_seen DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        nodes = []
        for row in rows:
            nodes.append({
                "id": row[0],
                "lat": float(row[1]),
                "lon": float(row[2]),
                "soil": row[3] or "--",
                "battery": row[4] or "--",
                "last_seen": str(row[5])
            })
        return jsonify(nodes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
