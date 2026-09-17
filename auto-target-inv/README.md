# Inventory Sizing - GitHub Pages

## Files

- `index.html`: Web dashboard standalone, bao gồm Home, Mass Load, Sync All và toàn bộ 11 warehouse.
- `icon.png`: Favicon của website.
- `Code.gs`: Backend Sync All. File này không chạy trên GitHub Pages; dán nội dung vào Google Apps Script và deploy dạng Web App.

## Deploy GitHub Pages

1. Upload `index.html`, `icon.png` và file README này vào thư mục publish của repository.
2. Vào **Settings > Pages**.
3. Chọn **Deploy from a branch**, nhánh `main`, thư mục chứa các file này.
4. Mở URL GitHub Pages được cung cấp.

## Google Apps Script

1. Dán `Code.gs` vào project Apps Script hiện tại.
2. Trong **Project Settings > Script Properties**, đặt `SYNC_KEY`.
3. Deploy Web App với **Execute as: Me** và **Who has access: Anyone**.
4. Mỗi khi cập nhật `Code.gs`, chọn **Deploy > Manage deployments > Edit > New version > Deploy**.
5. Nhập URL `/exec` và Sync key trong trang **Sync Data**, nhấn **Test**, rồi **Sync All**.

Backend ghi vào spreadsheet `1KabgqaozTjxtIz8kotRL42RFF6Zev0oqZb7IxAePEws`.

Không đưa giá trị `SYNC_KEY` vào GitHub.
