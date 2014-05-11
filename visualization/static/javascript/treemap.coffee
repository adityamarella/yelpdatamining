google.load "visualization", "1", { packages: ["treemap"] }

google.setOnLoadCallback ->
  # Create and populate the data table.
  dataTable = google.visualization.arrayToDataTable data

  # Create and draw the visualization.
  tree = new google.visualization.TreeMap(
    document.getElementById('treemap-chart'))
  tree.draw dataTable,
    fontSize: 16
    maxColor: '#00dd00'
    midColor: '#00bb00'
    minColor: '#009900'

  google.visualization.events.addListener tree, 'select', ->
