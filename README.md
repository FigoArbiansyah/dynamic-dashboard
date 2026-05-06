# Dynamic Dashboard v2 — Odoo 17

**Author:** Figo Arbiansyah | [figo.my.id](https://www.figo.my.id)  
**Version:** 17.0.2.0.0  
**License:** LGPL-3

---

## Fitur Utama

| Fitur | Deskripsi |
|---|---|
| **1 Menu → 1 Dashboard** | Setiap dashboard dikonfigurasi ke menu tertentu |
| **Card Count** | Menampilkan jumlah record berdasarkan model + domain |
| **Card Sum** | Menampilkan total nilai dari field numerik |
| **Chart** | Bar, Line, Pie, Doughnut, Polar Area, Radar |
| **Drag & Drop** | Reorder komponen via SortableJS |
| **Config Dialog** | Tambah/edit komponen tanpa coding |
| **ACL per Dashboard** | Batasi akses per `res.groups` |
| **ACL per Komponen** | Kontrol visibilitas per komponen |
| **Multi-company** | `company_id` pada setiap dashboard |
| **Click Action** | Card bisa redirect ke list view dengan domain terkait |

---

## Instalasi

1. Copy folder `dynamic_dashboard` ke direktori `addons` Odoo Anda.
2. Restart Odoo server:
   ```bash
   ./odoo-bin -u dynamic_dashboard -d <your_db>
   ```
3. Aktifkan module dari **Apps** → search `Dynamic Dashboard`.

---

## Cara Penggunaan

### 1. Buat Dashboard
- Buka **Dynamic Dashboard → Configuration → Dashboards**
- Klik **New**, isi nama, pilih menu target, atur grup akses.

### 2. Tambah Komponen
Ada dua cara:
- **Backend:** Buka form dashboard → tab Components → tambah baris.
- **Frontend (UI):** Buka dashboard → klik **Edit Layout** → **Add Component**.

### 3. Konfigurasi Card Count
- Type: `Card — Count`
- Model: pilih model Odoo (misal `sale.order`)
- Domain: `[['state','=','sale']]`
- Label, warna, icon: sesuaikan.

### 4. Konfigurasi Card Sum
- Type: `Card — Sum`
- Model + Domain seperti di atas
- Sum Field: pilih field numerik (misal `amount_total`)
- Prefix/Suffix: misal `Rp` / `,00`

### 5. Konfigurasi Chart
- Type: `Chart`
- Model + Domain
- Group By: field pengelompokan (misal `state`, `partner_id`)
- Measure: field numerik (kosongkan = count)
- Chart Type: bar / line / pie / doughnut / polarArea / radar

### 6. Drag & Drop Layout
- Klik **Edit Layout** di header dashboard.
- Drag komponen ke posisi baru.
- Posisi tersimpan otomatis.

---

## Struktur File

```
dynamic_dashboard/
├── controllers/
│   └── dashboard_controller.py     JSON-RPC endpoints
├── models/
│   ├── dashboard_board.py          Model utama dashboard
│   ├── dashboard_component.py      Komponen (card/chart)
│   └── dashboard_card_config.py    Config lanjutan (threshold, format)
├── security/
│   ├── dashboard_security.xml      Groups & ir.rule
│   └── ir.model.access.csv
├── static/src/components/
│   ├── dashboard/                  Root OWL component
│   ├── card_metric/                Card Count & Sum
│   ├── chart_widget/               Chart.js wrapper
│   └── config_dialog/              Dialog konfigurasi
├── views/
│   ├── dashboard_board_views.xml
│   ├── dashboard_component_views.xml
│   └── menu_views.xml
└── __manifest__.py
```

---

## API Endpoints

| Endpoint | Method | Deskripsi |
|---|---|---|
| `/dynamic_dashboard/get_data/<board_id>` | JSON | Load data dashboard |
| `/dynamic_dashboard/save_layout` | JSON | Simpan posisi grid |
| `/dynamic_dashboard/save_component` | JSON | Buat/update komponen |
| `/dynamic_dashboard/delete_component` | JSON | Hapus komponen |
| `/dynamic_dashboard/refresh_component` | JSON | Refresh data 1 komponen |
| `/dynamic_dashboard/get_model_fields` | JSON | List fields dari model |
| `/dynamic_dashboard/get_available_models` | JSON | List semua model |

---

## Grup Akses

| Group | Hak Akses |
|---|---|
| `Dashboard User` | Lihat dashboard (sesuai group assignment) |
| `Dashboard Manager` | Buat, edit, hapus dashboard & komponen |

---

## Pengembangan Lanjutan (Roadmap)

- [ ] Caching layer (Redis / Odoo cache) per TTL
- [ ] Trend indicator (vs last period)
- [ ] Conditional formatting (warning/danger threshold)
- [ ] Export dashboard sebagai PDF
- [ ] Widget filter date range global
- [ ] Responsive layout untuk mobile
