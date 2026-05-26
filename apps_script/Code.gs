/**
 * Apps Script web app: appends a lead row sent by the bot.
 * Setup: add Script Property SHARED_SECRET (= SHEETS_SHARED_SECRET), set the
 * spreadsheet time zone (File > Settings), deploy as Web app (Execute as: Me,
 * Access: Anyone), and put the /exec URL in SHEETS_WEBAPP_URL.
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

var AI_INTEREST_COL = 7;
var DECISION_COL = 8;

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
      _setupHeader(sheet);
    }

    var row = COLUMNS.map(function (key) {
      if (key === 'date') return new Date();
      if (key === 'telegram_user') return _userCell(lead[key]);
      if (key === 'ai_interest') return lead[key] === true;
      var value = lead[key];
      return value === undefined || value === null ? '' : value;
    });
    sheet.appendRow(row);

    // Basic filters do not re-evaluate programmatic appends, so re-assert the
    // default criteria on every insert to keep non-matching rows hidden.
    _applyDefaultFilter(sheet);

    return _json({ ok: true });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

function doGet() {
  return _json({ ok: true, service: 'telegramleadsbot-sheets' });
}

function _userCell(user) {
  if (!user) return '';
  var s = String(user);
  if (s.charAt(0) === '@') {
    var handle = s.substring(1);
    return '=HYPERLINK("https://t.me/' + handle + '","' + s + '")';
  }
  return s;
}

function _setupHeader(sheet) {
  sheet.appendRow(COLUMNS);

  var header = sheet.getRange(1, 1, 1, COLUMNS.length);
  header.setFontWeight('bold').setBackground('#1f2937').setFontColor('#ffffff');
  sheet.setFrozenRows(1);

  sheet.getRange(2, 1, sheet.getMaxRows() - 1, 1).setNumberFormat('yyyy-mm-dd hh:mm:ss');

  var widths = [150, 140, 320, 130, 90, 120, 90, 120, 360];
  for (var i = 0; i < widths.length; i++) {
    sheet.setColumnWidth(i + 1, widths[i]);
  }
}

function _applyDefaultFilter(sheet) {
  var filter = sheet.getFilter();
  if (!filter) {
    filter = sheet.getRange(1, 1, sheet.getMaxRows(), COLUMNS.length).createFilter();
  }
  filter.setColumnFilterCriteria(
    DECISION_COL,
    SpreadsheetApp.newFilterCriteria().setHiddenValues(['Not qualified']).build()
  );
  filter.setColumnFilterCriteria(
    AI_INTEREST_COL,
    SpreadsheetApp.newFilterCriteria().setHiddenValues(['FALSE']).build()
  );
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
