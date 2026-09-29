# ============================================================
#  app.py — เว็บแอป Flask (ทำให้เสร็จแล้ว ★ ปกติไม่ต้องแก้)
#  รัน:  python app.py  แล้วเปิด http://127.0.0.1:5000
#  ★ เพิ่มรายงานใหม่ไม่ต้องแก้ไฟล์นี้ — ไปเพิ่มที่ REPORTS ท้าย db.py
# ============================================================
from datetime import date, datetime
from flask import Flask, request, jsonify, render_template
from flask.json.provider import DefaultJSONProvider
import db


class JSONProvider(DefaultJSONProvider):
    """- ส่งวันที่เป็นรูปแบบ YYYY-MM-DD ให้ช่อง <input type="date"> ในฟอร์มอ่านได้
       - ไม่เรียงชื่อคอลัมน์ใหม่ → หัวตารางเรียงตามลำดับใน SELECT"""
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return DefaultJSONProvider.default(o)


app = Flask(__name__)
app.json = JSONProvider(app)


def safe(fn, *args, **kwargs):
    try:
        return jsonify({"ok": True, "data": fn(*args, **kwargs)})
    except NotImplementedError as e:
        return jsonify({"ok": False, "todo": True, "error": str(e)}), 501
    except ValueError as e:
        # ข้อผิดพลาดที่ db.py ตั้งใจแจ้งผู้ใช้ เช่น raise ValueError("หนังสือถูกยืมหมดแล้ว")
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


@app.route("/")
def page_home():
    return render_template("index.html")

@app.route("/report")
def page_report():
    return render_template("report.html")


# ---- สมาชิก ----
@app.route("/api/members", methods=["GET"])
def members_list():

    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_members, filters)

@app.route("/api/members/<int:_id>", methods=["GET"])
def member_get(_id):
    return safe(db.get_member, _id)

@app.route("/api/members", methods=["POST"])
def member_create():
    return safe(db.create_member, request.json)

@app.route("/api/members/<int:_id>", methods=["PUT"])
def member_update(_id):
    return safe(db.update_member, _id, request.json)

@app.route("/api/members/<int:_id>", methods=["DELETE"])
def member_delete(_id):
    return safe(db.delete_member, _id)

# ---- หนังสือ ----
@app.route("/api/books", methods=["GET"])
def books_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_books, filters)

@app.route("/api/books/<int:_id>", methods=["GET"])
def book_get(_id):
    return safe(db.get_book, _id)

@app.route("/api/books", methods=["POST"])
def book_create():
    return safe(db.create_book, request.json)

@app.route("/api/books/<int:_id>", methods=["PUT"])
def book_update(_id):
    return safe(db.update_book, _id, request.json)

@app.route("/api/books/<int:_id>", methods=["DELETE"])
def book_delete(_id):
    return safe(db.delete_book, _id)

# ---- การยืม/คืน ----
@app.route("/api/borrows", methods=["GET"])
def borrows_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_borrows, filters)

@app.route("/api/borrows/<int:_id>", methods=["GET"])
def borrow_get(_id):
    return safe(db.get_borrow, _id)

@app.route("/api/borrows", methods=["POST"])
def borrow_create():
    return safe(db.create_borrow, request.json)

@app.route("/api/borrows/<int:_id>", methods=["PUT"])
def borrow_update(_id):
    return safe(db.update_borrow, _id, request.json)

@app.route("/api/borrows/<int:_id>", methods=["DELETE"])
def borrow_delete(_id):
    return safe(db.delete_borrow, _id)

# ---- หมวดหมู่ ----
@app.route("/api/categories", methods=["GET"])
def categories_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_categories, filters)

@app.route("/api/categories/<int:_id>", methods=["GET"])
def category_get(_id):
    return safe(db.get_category, _id)

@app.route("/api/categories", methods=["POST"])
def category_create():
    return safe(db.create_category, request.json)

@app.route("/api/categories/<int:_id>", methods=["PUT"])
def category_update(_id):
    return safe(db.update_category, _id, request.json)

@app.route("/api/categories/<int:_id>", methods=["DELETE"])
def category_delete(_id):
    return safe(db.delete_category, _id)


# ---- รายงาน ----
@app.route("/api/reports/summary")
def report_summary():
    return safe(db.report_summary)

@app.route("/api/reports")
def report_list():
    """รายชื่อรายงานทั้งหมด (อ่านจาก db.REPORTS) ให้หน้าเว็บสร้างกล่องรายงาน"""
    return jsonify({"ok": True, "data": [{"key": k, "title": t} for k, t, _ in db.REPORTS]})

@app.route("/api/reports/<key>")
def report_run(key):
    """รันรายงานตามชื่อ เช่น /api/reports/overdue"""
    for k, _, fn in db.REPORTS:
        if k == key:
            return safe(fn)
    return jsonify({"ok": False, "error": f"ไม่พบรายงาน '{key}' ใน db.REPORTS"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
