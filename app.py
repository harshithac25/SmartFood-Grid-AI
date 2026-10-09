from flask import Flask, render_template, request, jsonify
import sqlite3, math
from pathlib import Path
from datetime import date
app=Flask(__name__)
DB=Path(__file__).with_name("smartfood.db")
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 with db() as c:
  c.execute("""CREATE TABLE IF NOT EXISTS food(id INTEGER PRIMARY KEY AUTOINCREMENT, donor TEXT, food_name TEXT, quantity_kg REAL, expiry_date TEXT, latitude REAL, longitude REAL, contact TEXT DEFAULT '', status TEXT DEFAULT 'available')""")
  c.execute("""CREATE TABLE IF NOT EXISTS rescues(id INTEGER PRIMARY KEY AUTOINCREMENT, food_id INTEGER, quantity_kg REAL)""")
  if c.execute("SELECT COUNT(*) FROM food").fetchone()[0]==0:
   c.executemany("INSERT INTO food(donor,food_name,quantity_kg,expiry_date,latitude,longitude) VALUES(?,?,?,?,?,?)",[
   ("Green Leaf Cafe","Cooked rice and curry",12,"2027-12-31",17.385,78.4867),("Sunrise Bakery","Bread and buns",8,"2027-12-31",17.392,78.481),("Community Hall","Packed meal boxes",20,"2027-12-31",17.370,78.500)])
def dist(a,b,x,y):
 r=6371; p=math.pi/180
 z=math.sin((x-a)*p/2)**2+math.cos(a*p)*math.cos(x*p)*math.sin((y-b)*p/2)**2
 return 2*r*math.asin(math.sqrt(z))
@app.get("/")
def home(): return render_template("index.html")
@app.get("/api/food")
def foods():
 with db() as c: rows=c.execute("SELECT * FROM food ORDER BY id DESC").fetchall()
 return jsonify([dict(x) for x in rows])
@app.post("/api/food")
def add():
 d=request.get_json() or {}
 try:
  q=float(d["quantity_kg"]); lat=float(d["latitude"]); lon=float(d["longitude"]); date.fromisoformat(d["expiry_date"])
  if q<=0 or not -90<=lat<=90 or not -180<=lon<=180: raise ValueError()
 except (KeyError,ValueError,TypeError): return jsonify(error="Check quantity, date, latitude and longitude."),400
 with db() as c:
  cur=c.execute("INSERT INTO food(donor,food_name,quantity_kg,expiry_date,latitude,longitude,contact) VALUES(?,?,?,?,?,?,?)",(d["donor"].strip(),d["food_name"].strip(),q,d["expiry_date"],lat,lon,d.get("contact","")))
 return jsonify(message="Food listing added.",id=cur.lastrowid),201
@app.get("/api/match")
def match():
 try: lat=float(request.args.get("latitude",17.385)); lon=float(request.args.get("longitude",78.4867)); radius=min(100,max(1,float(request.args.get("radius",10))))
 except ValueError: return jsonify(error="Coordinates and radius must be numbers."),400
 with db() as c: rows=c.execute("SELECT * FROM food WHERE status='available' AND quantity_kg>0 AND expiry_date>=?",(date.today().isoformat(),)).fetchall()
 out=[]
 for row in rows:
  item=dict(row); d=dist(lat,lon,item["latitude"],item["longitude"])
  if d<=radius: item["distance_km"]=round(d,2); out.append(item)
 return jsonify(sorted(out,key=lambda x:x["distance_km"]))
@app.post("/api/rescue")
def rescue():
 d=request.get_json() or {}
 try: fid=int(d["food_id"]); q=float(d["quantity_kg"]); assert q>0
 except (KeyError,ValueError,TypeError,AssertionError): return jsonify(error="Enter a valid ID and positive quantity."),400
 with db() as c:
  item=c.execute("SELECT * FROM food WHERE id=?",(fid,)).fetchone()
  if not item: return jsonify(error="Listing not found."),404
  if item["status"]!="available" or q>item["quantity_kg"]: return jsonify(error="Quantity is not available."),400
  remain=round(item["quantity_kg"]-q,3)
  c.execute("INSERT INTO rescues(food_id,quantity_kg) VALUES(?,?)",(fid,q))
  c.execute("UPDATE food SET quantity_kg=?,status=? WHERE id=?",(remain,"rescued" if remain==0 else "available",fid))
 return jsonify(message=f"{q:g} kg rescued.",remaining_kg=remain)
@app.get("/api/dashboard")
def dashboard():
 with db() as c:
  available=c.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM food WHERE status='available'").fetchone()[0]
  rescued=c.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM rescues").fetchone()[0]
  donors=c.execute("SELECT COUNT(DISTINCT donor) FROM food").fetchone()[0]
 return jsonify(listed_kg=round(available+rescued,1),available_kg=round(available,1),rescued_kg=round(rescued,1),donors=donors)
if __name__=="__main__":
 init(); print("Open http://127.0.0.1:5000"); app.run(debug=True)
