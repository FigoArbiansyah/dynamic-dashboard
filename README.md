# Dynamic Dashboard — Odoo 17

> **Configurable analytics dashboard** built with OWL (Odoo Web Library) and Chart.js.  
> Supports Card Count, Card Sum, and interactive Charts — all configurable without coding.

**Author:** Figo Arbiansyah · [figo.my.id](https://www.figo.my.id)  
**Version:** `17.0.2.0.0`  
**License:** LGPL-3  
**Depends:** `base`, `web`

---

## Daftar Isi

1. [Fitur Utama](#fitur-utama)
2. [Arsitektur Modul](#arsitektur-modul)
3. [Instalasi](#instalasi)
4. [Cara Penggunaan](#cara-penggunaan)
   - [Buat Dashboard](#1-buat-dashboard)
   - [Tambah Komponen](#2-tambah-komponen)
   - [Card — Count](#3-card--count)
   - [Card — Sum](#4-card--sum)
   - [Chart](#5-chart)
   - [Drag & Drop Layout](#6-drag--drop-layout)
5. [Struktur File](#struktur-file)
6. [Model & Field](#model--field)
   - [dashboard.board](#dashboardboard)
   - [dashboard.component](#dashboardcomponent)
   - [dashboard.card.config](#dashboardcardconfig)
7. [API Endpoints (JSON-RPC)](#api-endpoints-json-rpc)
8. [Kontrol Akses (ACL)](#kontrol-akses-acl)
9. [Catatan Upgrade (Pre-Init Hook)](#catatan-upgrade-pre-init-hook)
10. [Roadmap](#roadmap)

---

## Fitur Utama

| # | Fitur | Deskripsi |
|---|---|---|
| 1 | **Card Count** | Menampilkan jumlah record berdasarkan model + domain filter |
| 2 | **Card Sum** | Menampilkan total nilai field numerik (integer / float / monetary) |
| 3 | **Chart** | Bar, Line, Pie, Doughnut, Polar Area, Radar via Chart.js |
| 4 | **Card Style** | 4 varian tampilan: Solid, Outline, Gradient, Soft |
| 5 | **Click Action** | Card dapat membuka list view dengan domain terkait |
| 6 | **Prefix / Suffix** | Nilai card dapat diformat dengan prefix (`Rp`) dan suffix (`,-`) |
| 7 | **Icon Kustom** | FontAwesome icon per komponen (contoh: `fa-users`, `fa-dollar-sign`) |
| 8 | **Drag & Drop** | Reorder komponen via SortableJS, posisi tersimpan otomatis |
| 9 | **Config Dialog** | Tambah / edit komponen langsung dari UI tanpa coding |
| 10 | **ACL per Dashboard** | Batasi akses dashboard per `res.groups` |
| 11 | **ACL per Komponen** | Visibilitas komponen dikontrol per grup secara independen |
| 12 | **Multi-Company** | `company_id` pada setiap dashboard; isolasi data antar perusahaan |
| 13 | **Auto Menu** | Pembuatan menu & `ir.actions.client` otomatis saat dashboard dibuat |
| 14 | **Cache TTL** | Field `cache_ttl` (detik) siap digunakan untuk layer caching |
| 15 | **Error Isolation** | Komponen yang gagal load ditampilkan sebagai error card; komponen lain tetap berjalan |

---

## Arsitektur Modul

```
┌─────────────────────────────────────────────────────────┐
│                   Odoo Backend (Python)                 │
│                                                         │
│  dashboard.board ──► dashboard.component                │
│       │                    │                            │
│       │              dashboard.card.config              │
│       │                                                 │
│  DynamicDashboardController (JSON-RPC)                  │
│    /get_data, /save_layout, /save_component, ...        │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP JSON
┌─────────────────────────▼───────────────────────────────┐
│              OWL Frontend (JavaScript)                   │
│                                                         │
│  DashboardClientAction                                   │
│    └── DashboardRoot                                     │
│          ├── CardMetric  (card_count / card_sum)         │
│          ├── ChartWidget (Chart.js wrapper)              │
│          └── ConfigDialog (modal tambah/edit komponen)  │
└─────────────────────────────────────────────────────────┘
```

---

## Instalasi

### Prasyarat

- Odoo `17.0`
- Python ≥ 3.10
- Module: `base`, `web`

### Langkah Instalasi

1. **Copy modul** ke direktori `addons`:
   ```bash
   cp -r dynamic_dashboard /path/to/odoo/addons/
   ```

2. **Restart Odoo** dan upgrade modul:
   ```bash
   ./odoo-bin -u dynamic_dashboard -d <nama_database>
   ```

3. **Aktifkan** dari menu **Apps** → cari `Dynamic Dashboard` → klik **Install**.

> **Catatan Upgrade:** Modul ini memiliki `pre_init_hook` yang secara otomatis membersihkan record `ir.ui.view` dan `ir.actions.act_window` orphan dari versi lama sebelum upgrade dijalankan. Lihat [Catatan Upgrade](#catatan-upgrade-pre-init-hook).

---

## Cara Penggunaan

### 1. Buat Dashboard

1. Buka **Dynamic Dashboard → Configuration → Dashboards**.
2. Klik **New**.
3. Isi field berikut:

   | Field | Keterangan |
   |---|---|
   | **Dashboard Name** | Nama dashboard (wajib) |
   | **Parent Menu** | Lokasi menu di sidebar (default: root Dynamic Dashboard) |
   | **Access Groups** | Kosongkan = semua user; isi = hanya grup tertentu |
   | **Company** | Perusahaan pemilik dashboard |
   | **Cache TTL** | Durasi cache data komponen dalam detik (0 = nonaktif) |

4. **Simpan** → menu baru dan `ir.actions.client` dibuat otomatis.

---

### 2. Tambah Komponen

Ada **dua cara** menambah komponen:

**A. Melalui Backend (Form)**
- Buka form dashboard → tab **Components** → klik **Add a line**.

**B. Melalui UI Frontend**
- Buka dashboard di menu → klik **Edit Layout** → klik **Add Component**.

---

### 3. Card — Count

Menampilkan jumlah record yang memenuhi domain tertentu.

```
Type    : Card — Count
Model   : sale.order
Domain  : [['state', '=', 'sale']]
Label   : SO Confirmed
Icon    : fa-file-invoice
Color   : #4F46E5
Style   : Solid | Outline | Gradient | Soft
```

---

### 4. Card — Sum

Menampilkan total nilai field numerik.

```
Type         : Card — Sum
Model        : sale.order
Domain       : [['state', '=', 'sale']]
Measure Field: amount_total
Prefix       : Rp
Suffix       : ,-
Label        : Total Revenue
```

---

### 5. Chart

Menampilkan visualisasi data dalam berbagai jenis grafik.

```
Type        : Chart
Model       : fleet.vehicle
Domain      : []
Group By    : state_id
Measure     : (kosong = count)
Chart Type  : bar | line | pie | doughnut | polarArea | radar
Show Legend : ✓
```

> **Tips:** Jika *Group By* dikosongkan, chart menampilkan satu bar/slice berisi total count atau sum dari seluruh record.

---

### 6. Drag & Drop Layout

1. Klik **Edit Layout** di header dashboard.
2. Drag komponen ke posisi yang diinginkan.
3. Posisi `x`, `y`, `w` (lebar kolom), `h` (tinggi baris) tersimpan otomatis ke database via endpoint `/dynamic_dashboard/save_layout`.

---

## Struktur File

```
dynamic_dashboard/
├── controllers/
│   └── dashboard_controller.py      # 8 JSON-RPC endpoint
├── models/
│   ├── __init__.py
│   ├── dashboard.py                 # Model lama (dashboard.board & dashboard.chart) — legacy
│   ├── dashboard_board.py           # Model utama: dashboard.board
│   ├── dashboard_component.py       # Model komponen: dashboard.component
│   └── dashboard_card_config.py     # Advanced config: threshold, trend, format angka
├── security/
│   ├── dashboard_security.xml       # Groups & ir.rule (user / manager / multi-company)
│   └── ir.model.access.csv          # CRUD permission per model
├── static/src/
│   ├── components/
│   │   ├── dashboard/               # Root OWL component + action client tag
│   │   ├── card_metric/             # Card Count & Card Sum renderer
│   │   ├── chart_widget/            # Chart.js integration
│   │   ├── chart/                   # Chart helper utilities
│   │   └── config_dialog/           # Modal dialog konfigurasi komponen
│   ├── img/                         # Aset gambar
│   └── scss/
│       └── dashboard.scss           # Styling dashboard & komponen
├── views/
│   ├── dashboard_board_views.xml    # Form & tree view dashboard.board
│   ├── dashboard_component_views.xml# Form & tree view dashboard.component
│   ├── dashboard_chart_views.xml    # View legacy (dashboard.chart)
│   ├── dashboard_views.xml          # View legacy (dashboard.board lama)
│   └── menu_views.xml               # Menu item statis
├── hooks.py                         # pre_init_hook: cleanup orphan records
└── __manifest__.py
```

---

## Model & Field

### `dashboard.board`

Model utama yang merepresentasikan satu dashboard.

| Field | Tipe | Keterangan |
|---|---|---|
| `name` | Char | Nama dashboard (wajib) |
| `menu_id` | Many2one(`ir.ui.menu`) | Menu yang ditautkan (auto-generate) |
| `menu_parent_id` | Many2one(`ir.ui.menu`) | Induk menu; default ke root modul ini |
| `dashboard_action_id` | Many2one(`ir.actions.client`) | Client action yang dibuat otomatis |
| `group_ids` | Many2many(`res.groups`) | Grup yang diizinkan mengakses; kosong = semua |
| `company_id` | Many2one(`res.company`) | Perusahaan pemilik |
| `is_active` | Boolean | Status aktif/nonaktif dashboard |
| `layout_json` | Text | JSON array posisi grid komponen |
| `cache_ttl` | Integer | Durasi cache data (detik); 0 = nonaktif |
| `component_ids` | One2many(`dashboard.component`) | Daftar komponen |
| `component_count` | Integer (compute) | Jumlah komponen (tampil di form) |

**Auto Menu Sync:** Saat dashboard dibuat atau field `name`, `menu_parent_id`, `group_ids`, atau `is_active` diubah, modul secara otomatis mensinkronkan `ir.ui.menu` dan `ir.actions.client` terkait.

---

### `dashboard.component`

Setiap baris komponen dalam satu dashboard.

| Field | Tipe | Keterangan |
|---|---|---|
| `board_id` | Many2one(`dashboard.board`) | Dashboard induk |
| `name` | Char | Nama komponen (wajib) |
| `type` | Selection | `card_count` / `card_sum` / `chart` |
| `sequence` | Integer | Urutan tampil |
| `is_active` | Boolean | Sembunyikan tanpa hapus |
| `model_id` | Many2one(`ir.model`) | Model sumber data |
| `model_name` | Char (related) | Nama teknis model (store=True) |
| `domain` | Char | Domain filter Odoo (contoh: `[['state','=','sale']]`) |
| `measure_field_id` | Many2one(`ir.model.fields`) | Field numerik untuk sum / measure chart |
| `group_by_field_id` | Many2one(`ir.model.fields`) | Field group by untuk chart |
| `label` | Char | Judul yang tampil di card/chart |
| `color` | Char | Warna hex (default: `#4F46E5`) |
| `card_style` | Selection | `solid` / `outline` / `gradient` / `soft` |
| `icon` | Char | FontAwesome class (contoh: `fa-users`) |
| `click_action_id` | Many2one(`ir.actions.act_window`) | Action saat card diklik |
| `prefix` | Char | Teks sebelum nilai (contoh: `Rp`) |
| `suffix` | Char | Teks setelah nilai (contoh: `,-`) |
| `chart_type` | Selection | `bar` / `line` / `pie` / `doughnut` / `polarArea` / `radar` |
| `chart_legend` | Boolean | Tampilkan legenda chart |
| `chart_label` | Char | Label dataset pada chart |
| `pos_x` | Integer | Posisi kolom di grid |
| `pos_y` | Integer | Posisi baris di grid |
| `pos_w` | Integer | Lebar dalam kolom (default: 4) |
| `pos_h` | Integer | Tinggi dalam baris (default: 2) |
| `group_ids` | Many2many(`res.groups`) | Grup yang dapat melihat komponen ini |

---

### `dashboard.card.config`

Model opsional untuk konfigurasi lanjutan per komponen card. Dipakai sebagai hook untuk fitur yang akan datang.

| Field | Tipe | Keterangan |
|---|---|---|
| `component_id` | Many2one(`dashboard.component`) | Komponen terkait |
| `threshold_warning` | Float | Nilai batas peringatan (kuning) |
| `threshold_danger` | Float | Nilai batas bahaya (merah) |
| `color_warning` | Char | Warna hex warning (default: `#F59E0B`) |
| `color_danger` | Char | Warna hex danger (default: `#EF4444`) |
| `color_success` | Char | Warna hex success (default: `#10B981`) |
| `show_trend` | Boolean | Tampilkan indikator tren |
| `trend_period` | Selection | `day` / `week` / `month` |
| `decimal_places` | Integer | Jumlah desimal (default: 0) |
| `number_format` | Selection | `none` / `comma` / `short` / `currency` |

---

## API Endpoints (JSON-RPC)

Semua endpoint menggunakan `type='json'`, `auth='user'`, `methods=['POST']`.

| Endpoint | Auth | Deskripsi |
|---|---|---|
| `POST /dynamic_dashboard/get_data/<board_id>` | User | Load seluruh data dashboard (komponen + layout) |
| `POST /dynamic_dashboard/save_layout` | Manager | Simpan posisi grid setelah drag & drop |
| `POST /dynamic_dashboard/save_component` | Manager | Buat atau update satu komponen |
| `POST /dynamic_dashboard/delete_component` | Manager | Hapus satu komponen |
| `POST /dynamic_dashboard/refresh_component` | User | Refresh data satu komponen |
| `POST /dynamic_dashboard/get_model_fields` | User | Ambil daftar field dari suatu model |
| `POST /dynamic_dashboard/get_available_models` | User | Ambil daftar semua model yang terinstall |

### Contoh: `get_data`

```javascript
// Request
await this.rpc('/dynamic_dashboard/get_data/1', {});

// Response
{
  "id": 1,
  "name": "Accounting Dashboard",
  "layout": [{"id": 5, "x": 0, "y": 0, "w": 4, "h": 2}],
  "components": [
    {
      "id": 5,
      "type": "card_count",
      "name": "Open Invoices",
      "label": "Open Invoices",
      "color": "#4F46E5",
      "card_style": "solid",
      "icon": "fa-file-invoice",
      "prefix": "",
      "suffix": "",
      "value": 42,
      "pos": {"x": 0, "y": 0, "w": 4, "h": 2},
      "click_action_id": 123,
      "click_domain": "[['state','=','posted']]",
      "click_model": "account.move"
    }
  ],
  "can_edit": true
}
```

### Contoh: `save_layout`

```javascript
await this.rpc('/dynamic_dashboard/save_layout', {
  board_id: 1,
  layout: [
    { id: 5, x: 0, y: 0, w: 4, h: 2 },
    { id: 6, x: 4, y: 0, w: 8, h: 2 },
  ]
});
// Response: { "status": "ok" }
```

---

## Kontrol Akses (ACL)

### Grup

| Grup | XML ID | Hak Akses |
|---|---|---|
| **Dashboard User** | `group_dashboard_user` | Lihat dashboard (sesuai group assignment) |
| **Dashboard Manager** | `group_dashboard_manager` | Buat, edit, hapus dashboard & komponen (sudah include User) |

### Record Rules

| Rule | Scope | Domain |
|---|---|---|
| **user group filter** | Dashboard User | Hanya board yang `group_ids` kosong atau user masuk dalam grup |
| **manager full access** | Dashboard Manager | Semua board `(1,'=',1)` |
| **multi-company** | Semua | Hanya board milik company user atau tanpa company |

### Catatan Keamanan

- Endpoint `/save_layout`, `/save_component`, `/delete_component` hanya dapat diakses oleh **Dashboard Manager**.
- `_user_can_access()` (board-level) dan `_user_has_access()` (komponen-level) diperiksa server-side pada setiap request data.

---

## Catatan Upgrade (Pre-Init Hook)

Versi lama modul memiliki file XML tambahan (`dashboard_views.xml`, `dashboard_chart_views.xml`) yang sudah dihapus dari manifest. Sisa record-nya di database dapat menyebabkan `ValueError` saat view loading.

`pre_init_hook` (di `hooks.py`) secara otomatis membersihkan:
- `ir_ui_view` orphan milik modul ini
- `ir_model_data` terkait view tersebut
- `ir_act_window` orphan (kecuali `action_dashboard_board` dan `action_dashboard_component`)

Hook ini dijalankan **sebelum** upgrade/install, sehingga aman untuk digunakan pada database existing.

---

## Roadmap

- [ ] **Caching layer aktif** — integrasi dengan Odoo cache / Redis berdasarkan `cache_ttl`
- [ ] **Trend indicator** — tampilkan perbandingan nilai vs periode sebelumnya
- [ ] **Conditional formatting** — warna otomatis berdasarkan `threshold_warning` / `threshold_danger` dari `dashboard.card.config`
- [ ] **Number formatting** — format `comma`, `short (K/M/B)`, `currency` dari `dashboard.card.config`
- [ ] **Export PDF** — export tampilan dashboard sebagai PDF
- [ ] **Global date range filter** — filter rentang tanggal yang berlaku untuk semua komponen
- [ ] **Responsive mobile layout** — breakpoint untuk tampilan di perangkat mobile

---

*Dokumentasi ini dibuat berdasarkan source code versi `17.0.2.0.0`. Selalu sinkronkan README ini saat ada perubahan signifikan pada model atau endpoint.*
