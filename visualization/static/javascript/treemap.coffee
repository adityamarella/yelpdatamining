dataTable = null
dataColumns = {}

google.load "visualization", "1", { packages: ["treemap"] }

google.setOnLoadCallback ->
  # Create and populate the data table.
  dataTable = google.visualization.arrayToDataTable data
  data[0].forEach (value, index) ->
    dataColumns[value] = index

  treemap_view = new google.visualization.DataView dataTable
  treemap_view.setColumns [
    dataColumns.category_title,
    dataColumns.parent_category,
    dataColumns.business_count,
    dataColumns.avg_review_count
  ]

  # Create and draw the visualization.
  treemap = new google.visualization.TreeMap document.getElementById('treemap-chart')
  treemap.draw treemap_view,
    fontColor: '#000000'
    fontSize: 16
    maxColorValue: 100
    # maxColor: '#f0ad4e'
    # midColor: '#999C8C'
    # minColor: '#428bca'
    minColorValue: 0
    showScale: true

  google.visualization.events.addListener treemap, 'select', ->
    selection = treemap.getSelection()
    row = selection[0].row
    console.log
      id: dataTable.getValue row, dataColumns.category_id
      title: dataTable.getValue row, dataColumns.category_title
