categoryDataTable = null
categoryDataColumns = {}
adjNounDataTable = null
selectedCategoryId = -1
treemap = null
adjNounCloud = null

google.load "visualization", "1", { packages: ["treemap"] }

google.setOnLoadCallback ->
  # Create and populate the data table.
  categoryDataTable = google.visualization.arrayToDataTable data
  data[0].forEach (value, index) ->
    categoryDataColumns[value] = index

  treemapView = new google.visualization.DataView categoryDataTable
  treemapView.setColumns [
    categoryDataColumns.category_title,
    categoryDataColumns.parent_category,
    categoryDataColumns.business_count,
    categoryDataColumns.avg_review_count
  ]

  # Create and draw the visualization.
  treemap = new google.visualization.TreeMap document.getElementById('treemap-chart')
  treemap.draw treemapView,
    fontColor: '#000000'
    fontSize: 16
    maxColorValue: 100
    # maxColor: '#f0ad4e'
    # midColor: '#999C8C'
    # minColor: '#428bca'
    minColorValue: 0
    showScale: true

  adjNounCloud = new TermCloud document.getElementById('adjnoun-tc')
  getSelectedCategoryId()
  updateAdjNoun(selectedCategoryId)

  google.visualization.events.addListener treemap, 'select', ->
    getSelectedCategoryId()
    console.log
      id: categoryDataTable.getValue selectedCategoryId, categoryDataColumns.category_id
      title: categoryDataTable.getValue selectedCategoryId, categoryDataColumns.category_title


getSelectedCategoryId = ->
  selection = treemap.getSelection()
  selectedCategoryId = selection[0]?.row ? -1
  return selectedCategoryId

updateAdjNoun = (categoryId) ->
  # url = "http://amarella-project-data.appspot.com/getinfo?mode=adjectivenoun&format=json&category=#{categoryId}"
  url = "http://amarella-project-data.appspot.com/getinfo?mode=adjectivenoun&format=json&category=1"

  jsonData = $.ajax(
    url: url,
    dataType: "json"
    async: false
  ).responseText

  # Create our data table out of JSON data loaded from server.
  adjNounDataTable = new google.visualization.DataTable jsonData
  adjNounDataView = new google.visualization.DataView adjNounDataTable
  adjNounDataView.setColumns [1, 2]

  # data = new google.visualization.DataTable()
  # data.addColumn('string', 'Label')
  # data.addColumn('number', 'Value')
  # data.addColumn('string', 'Link')
  # data.addRow(['Big', 100, ''])
  # data.addRow(['Small', 10, ''])

  adjNounCloud.draw adjNounDataView, null
