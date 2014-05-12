// Generated by CoffeeScript 1.7.1
(function() {
  var adjNounCloud, adjNounDataTable, categoryDataColumns, categoryDataTable, getSelectedCategoryRow, topicClouds, treemap, updateAdjNoun, updateCategoryTitle, updateTopics, updateVisualizations;

  categoryDataTable = null;

  categoryDataColumns = {};

  adjNounDataTable = null;

  treemap = null;

  adjNounCloud = null;

  topicClouds = [];

  google.load("visualization", "1", {
    packages: ["treemap"]
  });

  google.setOnLoadCallback(function() {
    var treemapView;
    categoryDataTable = google.visualization.arrayToDataTable(data);
    data[0].forEach(function(value, index) {
      return categoryDataColumns[value] = index;
    });
    treemapView = new google.visualization.DataView(categoryDataTable);
    treemapView.setColumns([categoryDataColumns.category_title, categoryDataColumns.parent_category, categoryDataColumns.business_count, categoryDataColumns.avg_review_count]);
    treemap = new google.visualization.TreeMap(document.getElementById('treemap-chart'));
    treemap.draw(treemapView, {
      fontColor: '#000000',
      fontSize: 16,
      maxColorValue: 100,
      minColorValue: 0,
      showScale: true
    });
    adjNounCloud = new TermCloud(document.getElementById('tc-adjnoun'));
    topicClouds = $('.tc-topic').map(function() {
      return new TermCloud(document.getElementById(this.id));
    }).get();
    updateVisualizations(0);
    google.visualization.events.addListener(treemap, 'select', function() {
      var selectedCategoryRow;
      selectedCategoryRow = getSelectedCategoryRow();
      return updateVisualizations(selectedCategoryRow);
    });
    return google.visualization.events.addListener(treemap, 'rollup', function() {
      var selectedCategoryRow;
      selectedCategoryRow = getSelectedCategoryRow();
      return updateVisualizations(selectedCategoryRow);
    });
  });

  getSelectedCategoryRow = function() {
    var selectedCategoryRow, selection, _ref, _ref1;
    selection = treemap.getSelection();
    selectedCategoryRow = (_ref = (_ref1 = selection[0]) != null ? _ref1.row : void 0) != null ? _ref : -1;
    console.log("selected category id: " + selectedCategoryRow);
    return selectedCategoryRow;
  };

  updateVisualizations = function(categoryRow) {
    var categoryId;
    categoryId = categoryDataTable.getValue(categoryRow, categoryDataColumns.category_id);
    updateCategoryTitle(categoryRow);
    updateAdjNoun(categoryId);
    return updateTopics(categoryId);
  };

  updateCategoryTitle = function(categoryRow) {
    var categoryTitle;
    categoryTitle = categoryDataTable.getValue(categoryRow, categoryDataColumns.category_title);
    return $('h2>span#category-title').text(categoryTitle);
  };

  updateAdjNoun = function(categoryId) {
    var adjNounDataView, jsonData, url;
    url = "http://amarella-project-data.appspot.com/getinfo?mode=adjectivenoun&format=json&category=" + categoryId;
    jsonData = $.ajax({
      url: url,
      dataType: "json",
      async: false
    }).responseText;
    adjNounDataTable = new google.visualization.DataTable(jsonData);
    adjNounDataView = new google.visualization.DataView(adjNounDataTable);
    adjNounDataView.setColumns([1, 2]);
    return adjNounCloud.draw(adjNounDataView, null);
  };

  updateTopics = function(categoryId) {
    var jsonData, topicsDataTable, topicsDataView, url;
    url = "http://amarella-project-data.appspot.com/getinfo?mode=topics&format=json&category=" + categoryId;
    jsonData = $.ajax({
      url: url,
      dataType: "json",
      async: false
    }).responseText;
    topicsDataTable = new google.visualization.DataTable(jsonData);
    topicsDataView = new google.visualization.DataView(topicsDataTable);
    topicsDataView.setColumns([1, 2]);
    return topicClouds.forEach(function(topicCloud, index) {
      var topicRows;
      topicRows = topicsDataTable.getFilteredRows([
        {
          column: 0,
          value: index
        }
      ]);
      topicsDataView.setRows(topicRows);
      return topicCloud.draw(topicsDataView, null);
    });
  };

}).call(this);
