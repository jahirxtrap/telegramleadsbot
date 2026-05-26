/**
 * Google Apps Script web app — receives leads from the bot and appends a row.
 *
 * Setup:
 *   1. Create a Google Sheet, then Extensions > Apps Script and paste this file.
 *   2. Project Settings > Script properties: add SHARED_SECRET = <same value as
 *      SHEETS_SHARED_SECRET in the bot's env>.
 *   3. Deploy > New deployment > Web app:
 *        - Execute as: Me
 *        - Who has access: Anyone
 *      Copy the /exec URL into the bot's SHEETS_WEBAPP_URL env var.
 *
 * The bot POSTs: { "secret": "...", "lead": { ...Lead fields... } }
 */

// Column order — must mirror the Lead model in schemas/lead.py.
var COLUMNS = [
  'captured_at',
  'telegram_user_id',
  'chat_id',
  'username',
  'full_name',
  'phone',
  'message',
  'intent',
  'qualified',
  'summary'
];

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var expected = PropertiesService.getScriptProperties().getProperty('SHARED_SECRET');

    if (!expected || body.secret !== expected) {
      return _json({ ok: false, error: 'forbidden' });
    }

    var lead = body.lead || {};
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(COLUMNS);
    }

    var row = COLUMNS.map(function (key) {
      var value = lead[key];
      return value === undefined || value === null ? '' : value;
    });
    sheet.appendRow(row);

    return _json({ ok: true });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

function doGet() {
  return _json({ ok: true, service: 'telegramleadsbot-sheets' });
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
