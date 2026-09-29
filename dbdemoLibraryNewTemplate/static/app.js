// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ (ทำให้เสร็จแล้ว ★ นิสิตไม่ต้องแก้)
//  ปรับช่องค้นหา/ฟอร์มได้ที่ตัวแปร ENTITIES ด้านล่าง
// ============================================================
// ตัวเลือกเพศ: value = ค่าที่เก็บใน database (ENUM), label = ข้อความที่แสดงบนหน้าจอ
const GENDERS = [{ "value": "female", "label": "หญิง" }, { "value": "male", "label": "ชาย" },
                  { "value": "non_binary", "label": "นอนไบนารี" }, { "value": "not_specified", "label": "ไม่ระบุ" }];

const ENTITIES = {
  "members": {
    "label": "สมาชิก",
    "api": "/api/members",
    "idKey": "member_id",
    "search": [
      { "key": "name", "label": "ชื่อ", "type": "text" },
      { "key": "email", "label": "อีเมล", "type": "text" },
      { "key": "gender", "label": "เพศ", "type": "select",
        "options": [{ "value": "", "label": "ทั้งหมด" }, ...GENDERS] },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["", "active", "inactive"] }
    ],
    "form": [
      { "key": "name", "label": "ชื่อ", "type": "text" },
      { "key": "gender", "label": "เพศ", "type": "select", "options": GENDERS },
      { "key": "email", "label": "อีเมล", "type": "text" },
      { "key": "phone", "label": "เบอร์โทร", "type": "text" },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["active", "inactive"] }
    ]
  },
  "books": {
    "label": "หนังสือ",
    "api": "/api/books",
    "idKey": "book_id",
    "search": [
      { "key": "title", "label": "ชื่อเรื่อง", "type": "text" },
      { "key": "author", "label": "ผู้แต่ง", "type": "text" },
      { "key": "category_id", "label": "หมวดหมู่", "type": "select",
        "optionsFrom": { "api": "/api/categories", "value": "category_id", "label": "name" } }
    ],
    "form": [
      { "key": "isbn", "label": "ISBN", "type": "text" },
      { "key": "title", "label": "ชื่อเรื่อง", "type": "text" },
      { "key": "author", "label": "ผู้แต่ง", "type": "text" },
      // dropdown แสดงชื่อหมวดหมู่ แต่ส่งค่าเป็น category_id (อ่านรายการจาก /api/categories)
      { "key": "category_id", "label": "หมวดหมู่", "type": "select",
        "optionsFrom": { "api": "/api/categories", "value": "category_id", "label": "name" } },
      { "key": "publish_year", "label": "ปีพิมพ์ (ค.ศ.)", "type": "number" },
      { "key": "quantity", "label": "จำนวนเล่ม", "type": "number" }
    ]
  },
  "borrows": {
    "label": "การยืม/คืน",
    "api": "/api/borrows",
    "idKey": "borrow_id",
    "search": [
      { "key": "member_id", "label": "รหัสสมาชิก", "type": "number" },
      { "key": "book_id", "label": "รหัสหนังสือ", "type": "number" },
      // สถานะไม่ได้เก็บในตาราง — db.py คำนวณจาก return_date / due_date
      { "key": "status", "label": "สถานะ", "type": "select", "options": [
          { "value": "", "label": "ทั้งหมด" }, { "value": "borrowed", "label": "กำลังยืม" },
          { "value": "overdue", "label": "เลยกำหนด" }, { "value": "returned", "label": "คืนแล้ว" }] }
    ],
    "form": [
      { "key": "book_id", "label": "รหัสหนังสือ", "type": "number" },
      { "key": "member_id", "label": "รหัสสมาชิก", "type": "number" },
      { "key": "borrow_date", "label": "วันที่ยืม", "type": "date" },
      { "key": "due_date", "label": "กำหนดคืน", "type": "date" },
      { "key": "return_date", "label": "วันที่คืน (เว้นว่างถ้ายังไม่คืน)", "type": "date" },
      // ---- ส่วนค่าปรับ: แสดงเฉพาะตอน "แก้ไข" (editOnly) — บันทึกลงตาราง fine ----
      { "type": "heading", "label": "💰 ค่าปรับ (เว้นว่างถ้าไม่มี)", "editOnly": true },
      { "key": "fine_amount", "label": "จำนวนเงิน (บาท)", "type": "number", "editOnly": true },
      { "key": "fine_paid", "label": "การชำระ", "type": "select", "editOnly": true,
        "options": [{ "value": "0", "label": "ยังไม่ชำระ" }, { "value": "1", "label": "ชำระแล้ว" }] },
      { "key": "fine_paid_date", "label": "วันที่ชำระ", "type": "date", "editOnly": true }
    ]
  },
  "categories": {
    "label": "หมวดหมู่",
    "api": "/api/categories",
    "idKey": "category_id",
    "search": [
      { "key": "name", "label": "ชื่อหมวดหมู่", "type": "text" }
    ],
    "form": [
      { "key": "name", "label": "ชื่อหมวดหมู่", "type": "text" },
      { "key": "description", "label": "คำอธิบาย", "type": "text" }
    ]
  }
};

let current = Object.keys(ENTITIES)[0];
let editingId = null;
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
  if (f.type === "heading") return '<div class="form-section">' + f.label + '</div>';
  let input;
  if (f.type === "select") {
    // options เป็นข้อความ "a" หรือ {value, label} ก็ได้
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
        return '<option value="' + v + '"' + (String(v) === String(value ?? "") ? " selected" : "") + '>' + t + '</option>';
      }).join("") + '</select>';
  } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">'; }
  return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}
// ช่อง select ที่มี optionsFrom → ดึงตัวเลือกจาก API (เช่น รายชื่อหมวดหมู่จากฐานข้อมูล)
async function loadOptions(fields, forSearch) {
  for (const f of fields.filter(f => f.optionsFrom)) {
    const src = f.optionsFrom, r = await api(src.api);
    f.options = r.ok ? (r.data || []).map(row => ({ value: row[src.value], label: row[src.label] }))
                     : [{ value: "", label: (r.todo ? "🚧 " : "⚠️ ") + r.error }];
    if (forSearch && r.ok) f.options.unshift({ value: "", label: "ทั้งหมด" });
  }
}
// ช่องในฟอร์มที่ใช้อยู่ตอนนี้ (ช่อง editOnly แสดงเฉพาะตอนแก้ไข)
function formFields() { return ENTITIES[current].form.filter(f => !f.editOnly || editingId !== null); }
async function buildSearch() {
  const cfg = ENTITIES[current];
  await loadOptions(cfg.search, true);
  if (cfg !== ENTITIES[current]) return;   // ผู้ใช้เปลี่ยนแท็บระหว่างรอ
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}
async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "กำลังค้นหา...");
  renderTable(await api(cfg.api + "?" + params.toString()));
}
function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) { setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + r.error, r.todo ? "todo" : "err"); return; }
  const rows = r.data || [];
  if (rows.length === 0) { setStatus(st, "ไม่พบข้อมูล"); return; }
  setStatus(st, "พบ " + rows.length + " รายการ");
  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => "<th>" + c + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = row[ENTITIES[current].idKey];
    return "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") +
      '<td><button class="btn sm" onclick="editRow(' + id + ')">แก้ไข</button> ' +
      '<button class="btn sm del" onclick="deleteRow(' + id + ')">ลบ</button></td></tr>';
  }).join("");
}
async function openForm(title, data = {}) {
  await loadOptions(formFields(), false);
  $("#modalTitle").textContent = title;
  $("#formFields").innerHTML = formFields().map(f => fieldHtml(f, "f_", data[f.key])).join("");
  $("#modal").classList.remove("hidden");
}
function collectForm() { const d = {}; formFields().filter(f => f.key).forEach(f => d[f.key] = $("#f_" + f.key).value); return d; }
async function editRow(id) {
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  editingId = id; openForm("แก้ไขข้อมูล", r.data);
}
async function deleteRow(id) {
  if (!confirm("ยืนยันการลบ?")) return;
  const r = await api(ENTITIES[current].api + "/" + id, { method: "DELETE" });
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  doSearch();
}
async function save() {
  const cfg = ENTITIES[current], data = collectForm();
  const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  $("#modal").classList.add("hidden"); doSearch();
}
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active"); current = t.dataset.entity;
  buildSearch(); $("#tableHead").innerHTML = ""; $("#tableBody").innerHTML = "";
  setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
}));
$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch();
$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");
buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
