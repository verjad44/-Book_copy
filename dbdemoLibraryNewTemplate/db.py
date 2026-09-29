# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
#  ดูตัวอย่างที่เขียนให้แล้ว: search_members, get_member
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- สมาชิก (member) ----------
def search_members(filters):
    """ค้นหา สมาชิก ตามเงื่อนไข (name, email, gender, status)
    ★ ตัวอย่างที่เขียนให้แล้ว — ใช้เป็นแบบสำหรับ search_xxx ตัวอื่น
    เริ่มจาก "WHERE 1=1" แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า
    ข้อความอิสระ (name, email) ใช้ LIKE %s / ค่าที่เป็นตัวเลือก (gender, status) ใช้ = %s
    ★ ถ้าใช้ gender LIKE '%male%' จะได้ female ด้วย เพราะคำว่า female มี male อยู่ข้างใน"""
    sql = "SELECT * FROM member WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("email"):
        sql += " AND email LIKE %s"
        params.append("%" + filters["email"] + "%")
    if filters.get("gender"):
        sql += " AND gender = %s"
        params.append(filters["gender"])
    if filters.get("status"):
        sql += " AND status = %s"
        params.append(filters["status"])
    sql += " ORDER BY member_id"
    return run_query(sql, params)


def get_member(member_id):
    """ดึง สมาชิก 1 รายการตาม member_id (ใช้ตอนเปิดฟอร์มแก้ไข)
    ★ ตัวอย่างที่เขียนให้แล้ว — ใช้เป็นแบบสำหรับ get_xxx ตัวอื่น"""
    rows = run_query("SELECT * FROM member WHERE member_id = %s", (member_id,))
    return rows[0] if rows else None


def create_member(data):
    sql = """INSERT INTO member (name, gender, email, phone, status)
             VALUES (%s, %s, %s, %s, %s)"""
    return run_command(sql, (data["name"], data["gender"], blank_to_none(data["email"]),data["phone"], data["status"]))


def update_member(member_id, data):
    sql = """UPDATE member
             SET name = %s, gender = %s, email = %s, phone = %s, status = %s
             WHERE member_id = %s"""
    return run_command(sql, (data["name"], data["gender"], blank_to_none(data["email"]),data["phone"], data["status"], member_id))


def delete_member(member_id):
    return run_command("DELETE FROM member WHERE member_id = %s", (member_id,))

# ---------- หนังสือ (book) ----------
# def search_books(filters):
#     """ค้นหา หนังสือ ตามเงื่อนไข (title, author, category_id)
#     ต้องแสดงคอลัมน์ (ตามลำดับ): book_id, isbn, title, author, category (ชื่อหมวด),
#                                publish_year, quantity, available
#     คำใบ้:
#       - JOIN category เพื่อแสดง *ชื่อ* หมวดหมู่แทนรหัส
#       - available (จำนวนที่ว่างให้ยืม) = quantity − จำนวนที่ยังไม่คืน (return_date IS NULL)
#         ไม่ได้เก็บเป็นคอลัมน์ → ต้องคำนวณ: LEFT JOIN กับ subquery  ที่นับเล่มที่ยังไม่คืนของแต่ละ book_id
#         แล้วใช้ IFNULL(..., 0) เพราะหนังสือที่ไม่มีคนยืมจะได้ NULL
#       - เงื่อนไข: title/author ใช้ LIKE %s, category_id ใช้ = %s (มาจาก dropdown)"""
#     # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
#     _todo("search_books")
def search_books(filters):
    sql = """select 	b.book_id               ,
		b.isbn 	            ,
		b.title             ,
		b.author            ,
		c.name		        AS 		category    ,
		b.publish_year      ,
        b.quantity          ,
        b.quantity - IFNULL(o.on_loan, 0)       AS available
        from 	        book b 
        inner 	join    category c on B.category_id = C.category_id 
        left    join    (SELECT book_id         , 
                        COUNT(*)                AS on_loan
                        FROM borrow
                        WHERE return_date IS NULL
                        GROUP BY book_id)       AS o 
        ON b.book_id = o.book_id
        where	1=1"""
    params = []
    if filters.get("title"):
                sql += " AND b.title LIKE %s"
                params.append("%" + filters["title"] + "%")
    if filters.get("author"):
                sql += " AND b.author LIKE %s"
                params.append("%" + filters["author"] + "%")
    if filters.get("category_id"):  
                sql += " AND b.category_id = %s"
                params.append(filters["category_id"])
    sql += " ORDER BY b.book_id"
    return run_query(sql, params)

    
def get_book(book_id):
    """ดึง หนังสือ 1 รายการตาม book_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM book WHERE book_id = %s", (book_id,))
    return rows[0] if rows else None


def create_book(data):
    """เพิ่ม หนังสือ ใหม่ — data มีคีย์: isbn, title, author, category_id, publish_year, quantity
    (category_id มาจาก dropdown หมวดหมู่ ซึ่งแสดงชื่อ แต่ส่งค่าเป็นรหัส)
    คำใบ้: isbn, publish_year ว่างได้ → ใช้ blank_to_none(...)"""
    sql = """INSERT INTO book (isbn, title, author, category_id, publish_year, quantity)
                 VALUES (%s, %s, %s, %s, %s)"""
    return run_command(sql, blank_to_none(data["isbn"], data["title"], (data["author"]),data["category_id"], blank_to_none(data["publish_year"]), data["quantity"]))


def update_book(book_id, data):
    """แก้ไข หนังสือ ตาม book_id"""
    sql = """UPDATE book
                 SET isbn = %s, title = %s, author = %s, category_id = %s, publish_year = %s, quantity = %s
                 WHERE book_id = %s"""
    return run_command(sql, blank_to_none(data["isbn"], data["title"], (data["author"]),data["category_id"], blank_to_none(data["publish_year"]), data["quantity"]), book_id)


def delete_book(book_id):
    """ลบ หนังสือ ตาม book_id"""
    return run_command("DELETE FROM book WHERE book_id = %s", (book_id,))

# ---------- การยืม/คืน (borrow + fine) ----------
# ★ ตาราง borrow ไม่มีคอลัมน์ status — สถานะคำนวณจากวันที่ (ไม่เก็บค่าที่คำนวณได้)
#     return_date มีค่า            → 'returned' (คืนแล้ว)
#     ยังไม่คืน และเลย due_date    → 'overdue'  (เลยกำหนด)
#     ยังไม่คืน และยังไม่เลยกำหนด  → 'borrowed' (กำลังยืม)

# def search_borrows(filters):
#     """ค้นหา การยืม ตามเงื่อนไข (member_id, book_id, status)
#     คำใบ้:
#       - JOIN member และ book เพื่อแสดงชื่อ, LEFT JOIN fine เพื่อแสดงค่าปรับ
#         (LEFT JOIN เพราะการยืมส่วนใหญ่ไม่มีค่าปรับ — ถ้าใช้ INNER JOIN แถวจะหายไป)
#       - คำนวณคอลัมน์ status ด้วย CASE:
#           CASE WHEN br.return_date IS NOT NULL THEN 'returned'
#                WHEN br.due_date < CURDATE()   THEN 'overdue'
#                ELSE 'borrowed' END AS status
#       - member_id, book_id ใช้ = %s
#       - filter "status" ไม่มีคอลัมน์ให้เทียบ → แปลงเป็นเงื่อนไขวันที่เอง เช่น
#           "returned" → AND br.return_date IS NOT NULL
#           "overdue"  → AND br.return_date IS NULL AND br.due_date < CURDATE()
#           "borrowed" → AND br.return_date IS NULL AND br.due_date >= CURDATE()"""
BORROW_STATUS_SQL = """CASE WHEN br.return_date IS NOT NULL     THEN 'returned'
                            WHEN br.due_date < CURDATE()        THEN 'overdue'
                            ELSE 'borrowed' END"""

def search_borrows(filters):
    sql = f"""SELECT    br.borrow_id    , 
                        br.member_id    ,   
                        m.name          AS member_name  ,
                        br.book_id      , 
                        b.title         , 
                        br.borrow_date  , 
                        br.due_date     , 
                        br.return_date  ,
                        {BORROW_STATUS_SQL}     AS status       ,
                        f.amount                AS fine_amount  , 
                        f.paid                  AS fine_paid
              FROM borrow br
              INNER JOIN    member m    ON br.member_id = m.member_id
              INNER JOIN    book   b    ON br.book_id   = b.book_id
              LEFT  JOIN    fine   f    ON br.borrow_id = f.borrow_id
              WHERE 1=1"""
    params = []
    if filters.get("member_id"):
        sql += " AND br.member_id = %s"
        params.append(filters["member_id"])
    if filters.get("book_id"):
        sql += " AND br.book_id = %s"
        params.append(filters["book_id"])
    # สถานะไม่ได้เก็บไว้ จึงแปลงเป็นเงื่อนไขวันที่แทน
    if filters.get("status") == "returned":
        sql += " AND br.return_date IS NOT NULL"
    elif filters.get("status") == "overdue":
        sql += " AND br.return_date IS NULL AND br.due_date < CURDATE()"
    elif filters.get("status") == "borrowed":
        sql += " AND br.return_date IS NULL AND br.due_date >= CURDATE()"
    sql += " ORDER BY br.borrow_id"
    return run_query(sql, params)
    

# def get_borrow(borrow_id):
#     """ดึง การยืม 1 รายการตาม borrow_id (ใช้ตอนเปิดฟอร์มแก้ไข)
#     ★ ฟอร์มแก้ไขมีช่องค่าปรับด้วย จึงต้องคืนคีย์: fine_amount, fine_paid, fine_paid_date
#     คำใบ้: SELECT br.*, f.amount AS fine_amount, f.paid AS fine_paid, f.paid_date AS fine_paid_date
#            FROM borrow br LEFT JOIN fine f ON br.borrow_id = f.borrow_id
#            WHERE br.borrow_id = %s"""
def get_borrow(borrow_id):
    sql = """SELECT br.*    , 
            f.amount        AS fine_amount  , 
            f.paid          AS fine_paid    , 
            f.paid_date     AS fine_paid_date
            FROM borrow br
            LEFT JOIN   fine f ON br.borrow_id = f.borrow_id
            WHERE br.borrow_id = %s"""
    rows = run_query(sql, (borrow_id,))
    return rows[0] if rows else None


# def check_can_borrow(book_id, member_id, borrow_id=None):
#     """ตรวจก่อนบันทึกการยืม — ถ้าไม่ผ่านให้ raise ValueError("ข้อความ")
#     (หน้าเว็บจะแสดงข้อความนั้นเป็น alert ให้ผู้ใช้เห็น)
#     1) สมาชิกต้องมีอยู่ และ status = 'active'
#        → SELECT name, status FROM member WHERE member_id = %s
#     2) หนังสือต้องเหลือว่าง (available > 0)
#        available = quantity − จำนวนแถวใน borrow ของหนังสือเล่มนี้ที่ return_date IS NULL
#        ★ ตอนแก้ไข (borrow_id ไม่ใช่ None) ต้องไม่นับรายการที่กำลังแก้อยู่: AND borrow_id <> %s
#     ตัวอย่าง: raise ValueError("หนังสือเล่มนี้ถูกยืมหมดแล้ว")"""
def check_can_borrow(book_id, member_id, borrow_id=None):
    rows = run_query("SELECT name, status FROM member WHERE member_id = %s", (member_id,))
    if not rows:
        raise ValueError(f"ไม่พบสมาชิกรหัส {member_id}")
    if rows[0]["status"] != "active":
        raise ValueError(f"สมาชิก {rows[0]['name']} ไม่ได้อยู่ในสถานะ active จึงยืมหนังสือไม่ได้")
    
    sql = """SELECT b.title,
                    b.quantity - (SELECT COUNT(*) FROM borrow br
                                  WHERE br.book_id = b.book_id
                                    AND br.return_date IS NULL
                                    AND br.borrow_id <> %s) AS available
             FROM book b
             WHERE b.book_id = %s"""
    rows = run_query(sql, (borrow_id or 0, book_id))
    if not rows:
        raise ValueError(f"ไม่พบหนังสือรหัส {book_id}")
    if rows[0]["available"] <= 0:
        raise ValueError(f"หนังสือ '{rows[0]['title']}' ถูกยืมหมดแล้ว (ว่าง 0 เล่ม)")


# def create_borrow(data):
#     """เพิ่ม การยืม ใหม่ — data มีคีย์: book_id, member_id, borrow_date, due_date, return_date
#     คำใบ้:
#       1) return_date ว่างได้ → return_date = blank_to_none(data.get("return_date"))
#       2) ถ้ายังไม่คืน (return_date เป็น None) → เรียก check_can_borrow(data["book_id"], data["member_id"]) ก่อน
#       3) INSERT INTO borrow (...) VALUES (%s, ...)"""
def create_borrow(data):
    return_date = blank_to_none(data.get("return_date"))
    if return_date is None:            # ยืมใหม่ที่ยังไม่คืน → ต้องมีเล่มว่าง
        check_can_borrow(data["book_id"], data["member_id"])
    sql = """INSERT INTO borrow (book_id, member_id, borrow_date, due_date, return_date)
             VALUES (%s, %s, %s, %s, %s)"""
    return run_command(sql, (data["book_id"], data["member_id"], data["borrow_date"],
                             data["due_date"], return_date))


# def update_borrow(borrow_id, data):
#     """แก้ไข การยืม/คืน ตาม borrow_id — ใช้ตอนบันทึกการคืนหนังสือด้วย
#     data มีคีย์: book_id, member_id, borrow_date, due_date, return_date
#                 และค่าปรับ: fine_amount, fine_paid ("0"/"1"), fine_paid_date
#     คำใบ้ 3 ขั้น:
#       0) (ตรวจว่ายืมได้) ถ้ารายการนี้ยังไม่คืน และมีการเปลี่ยน book_id / member_id
#          หรือเดิมคืนแล้วแต่ลบวันที่คืนออก → check_can_borrow(book_id, member_id, borrow_id)
#          (ดูค่าเดิมด้วย get_borrow(borrow_id) — บันทึกการคืน หรือแก้แค่ค่าปรับ ไม่ต้องตรวจ)
#       1) UPDATE borrow SET ... WHERE borrow_id=%s
#       2) ค่าปรับ (ตาราง fine มี borrow_id เป็น UNIQUE → 1 การยืมมีค่าปรับได้ 1 แถว)
#          - ถ้ากรอก fine_amount มา:
#              INSERT INTO fine (borrow_id, amount, paid, paid_date) VALUES (%s, %s, %s, %s)
#              ON DUPLICATE KEY UPDATE amount=VALUES(amount), paid=VALUES(paid), paid_date=VALUES(paid_date)
#          - ถ้า fine_amount ว่าง: DELETE FROM fine WHERE borrow_id=%s"""
def update_borrow(borrow_id, data):
    old = get_borrow(borrow_id)
    if old is None:
        raise ValueError(f"ไม่พบการยืมรหัส {borrow_id}")
    return_date = blank_to_none(data.get("return_date"))
    if return_date is None and (old["return_date"] is not None
                                or str(old["book_id"]) != str(data["book_id"])
                                or str(old["member_id"]) != str(data["member_id"])):
        check_can_borrow(data["book_id"], data["member_id"], borrow_id)

    sql = """UPDATE borrow
             SET book_id = %s, member_id = %s, borrow_date = %s, due_date = %s, return_date = %s
             WHERE borrow_id = %s"""
    out = run_command(sql, (data["book_id"], data["member_id"], data["borrow_date"],
                            data["due_date"], return_date, borrow_id))

    if blank_to_none(data.get("fine_amount")) is not None:
        sql = """INSERT INTO fine (borrow_id, amount, paid, paid_date)
                 VALUES (%s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE
                     amount = VALUES(amount), paid = VALUES(paid), paid_date = VALUES(paid_date)"""
        run_command(sql, (borrow_id, data["fine_amount"], data.get("fine_paid") or 0,
                          blank_to_none(data.get("fine_paid_date"))))
    else:
        run_command("DELETE FROM fine WHERE borrow_id = %s", (borrow_id,))
    return out


# def delete_borrow(borrow_id):
#     """ลบ การยืม ตาม borrow_id
#     คำใบ้: ต้องลบแถวใน fine ก่อน (เพราะ fine มี FOREIGN KEY ชี้มาที่ borrow)"""
def delete_borrow(borrow_id):
    run_command("DELETE FROM fine WHERE borrow_id = %s", (borrow_id,))
    return run_command("DELETE FROM borrow WHERE borrow_id = %s", (borrow_id,))

# ---------- หมวดหมู่ (category) ----------
def search_categories(filters):
    """ค้นหา หมวดหมู่ ตามเงื่อนไข (name)
    ★ ฟังก์ชันนี้ถูกใช้สร้าง dropdown หมวดหมู่ในแท็บหนังสือด้วย → ควรทำเป็นอันดับแรก ๆ
    คำใบ้: เริ่มจาก sql = "SELECT * FROM category WHERE 1=1" แล้วต่อ AND name LIKE %s, ORDER BY name"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_categories")


def get_category(category_id):
    """ดึง หมวดหมู่ 1 รายการตาม category_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM category WHERE category_id = %s แล้วคืนแถวเดียว
    _todo("get_category")


def create_category(data):
    """เพิ่ม หมวดหมู่ ใหม่ — data มีคีย์: name, description (name ห้ามซ้ำ เพราะเป็น UNIQUE)"""
    # TODO: INSERT INTO category (...) VALUES (%s, ...)
    _todo("create_category")


def update_category(category_id, data):
    """แก้ไข หมวดหมู่ ตาม category_id"""
    # TODO: UPDATE category SET ... WHERE category_id=%s
    _todo("update_category")


def delete_category(category_id):
    """ลบ หมวดหมู่ ตาม category_id (ถ้ายังมีหนังสือในหมวดนี้ MySQL จะไม่ยอมลบ เพราะ FOREIGN KEY)"""
    # TODO: DELETE FROM category WHERE category_id=%s
    _todo("delete_category")


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ
#    ใช้ AS ตั้งชื่อภาษาไทยได้ เช่น  SELECT b.title AS 'ชื่อหนังสือ'
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}  (1 คีย์ = 1 การ์ด)
    ตอนนี้ยังไม่ได้เขียน SQL → คืนค่า None ทุกการ์ด หน้าเว็บจึงแสดง "—" รอไว้
    ★ งานของนิสิต: เขียน SQL ตามตัวอย่างด้านล่าง (1 คอลัมน์ใน SELECT = 1 การ์ด
      ชื่อหลัง AS = ข้อความใต้ตัวเลข) แล้วลบ return {...} ชุดล่างสุดทิ้ง
    ★ การ์ด "คิดเพิ่มเอง" 2 ใบ: ตั้งชื่อการ์ดใหม่ แล้วเขียน SQL เอง
    ★ ผลรวมเงินใช้ IFNULL(SUM(...), 0) — ถ้ายังไม่มีข้อมูล SUM จะได้ NULL"""
    # ---- ตัวอย่างเมื่อเขียน SQL แล้ว (เอา # ข้างหน้าออก แล้วเติมให้ครบทุกการ์ด) ----
    # sql = """SELECT
    #            (SELECT COUNT(*) FROM ...) AS 'สมาชิก',
    #            (SELECT ...)               AS 'ชื่อหนังสือ',
    #            ...
    #          """
    # return run_query(sql)[0]      ← [0] = เอาแถวแรก (ผลมีแถวเดียว) ได้เป็น dict

    # TODO: ระหว่างที่ยังไม่ได้เขียน SQL คืนค่า None ให้การ์ดแสดง "—" รอไว้
    return {
        "สมาชิก":         None,   # (SELECT COUNT(*) FROM member)
        "ชื่อหนังสือ":    None,   # นับหนังสือทั้งหมด
        "กำลังยืม":       None,   # นับการยืมที่ยังไม่คืน (return_date IS NULL)
        "ค้างคืน":        None,   # ยังไม่คืน และเลยกำหนด (due_date < CURDATE())
        "คิดเพิ่มเอง 1":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
        "คิดเพิ่มเอง 2":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
    }

def report_popular_books():
    """📈 หนังสือยอดนิยม (Most Borrowed)
    คำใบ้: JOIN borrow→book→category, GROUP BY book, COUNT, ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_popular_books")

def report_overdue():
    """⏰ สมาชิกค้างคืน (Overdue)
    คำใบ้: JOIN borrow→member, borrow→book, WHERE return_date IS NULL AND due_date < CURDATE(),
           DATEDIFF(CURDATE(), due_date) = จำนวนวันที่เกิน
    ★ ลองคิด: ทำไมคำนวณจากวันที่ แทนการใช้ WHERE status = 'overdue' ?"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_overdue")

def report_members_above_avg():
    """🏅 สมาชิกที่ยืมมากกว่าค่าเฉลี่ย (Above Average)
    คำใบ้: JOIN borrow→member, GROUP BY member,
           HAVING COUNT(*) > (subquery หา AVG ของจำนวนการยืมต่อคน)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_members_above_avg")


# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-books",  "📈 หนังสือยอดนิยม (Most Borrowed)",              report_popular_books),
    ("overdue",        "⏰ สมาชิกค้างคืน (Overdue)",                    report_overdue),
    ("active-members", "🏅 สมาชิกที่ยืมมากกว่าค่าเฉลี่ย (Above Average)", report_members_above_avg),
    # ("unpaid-fines", "💰 ค่าปรับค้างชำระ", report_unpaid_fines),   ← ตัวอย่างการเพิ่มรายงานที่ 4
]
