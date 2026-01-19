# Troubleshooting

## Empty PDFs or HTML Error messages

- Verify session cookie validity
- Check tenant name
- Confirm ticket ID

## In the case of a payload being passed

- Values being escaped appropriately
- URL encoding there necessary special characters
- Look at specifications and error codes on payload mismatch

## HTTP 302 / 401 / 403

- Session expired
- Wrong tenant
- Insufficient permissions

## Enhancements

- buid library of payloads
- consider using python tools such as t strings / Jinja for templating
- consider implementing a bootstrap procedure

