/**
 * Apps Script web app: appends a lead row sent by the bot.
 * Setup: add Script Property SHARED_SECRET (= SHEETS_SHARED_SECRET), deploy as
 * Web app (Execute as: Me, Access: Anyone), put the /exec URL in SHEETS_WEBAPP_URL.
 */

// Must mirror the LeadRecord fields in schemas/lead.py.
var COLUMNS = [
  'date',
  'telegram_user',
  'received_text',
  'sector',
  'employees',
  'location',
  'ai_interest',
  'decision',
  'reason'
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
