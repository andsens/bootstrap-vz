class window.TaskOverview
	viewBoxHeight = 800
	viewBoxWidth = 200
	margins =
		top:    100
		left:   50
		bottom: 100
		right:  50
	gravity =
		lateral: .1
		longitudinal: .2

	length = ([x,y]) -> Math.sqrt(x*x + y*y)
	sum = ([x1,y1], [x2,y2]) -> [x1+x2, y1+y2]
	diff = ([x1,y1], [x2,y2]) -> [x1-x2, y1-y2]
	prod = ([x,y], scalar) -> [x*scalar, y*scalar]
	div = ([x,y], scalar) -> [x/scalar, y/scalar]
	unit = (vector) -> div(vector, length(vector))
	scale = (vector, scalar) -> prod(unit(vector), scalar)
	position = (coord, vector) -> [coord, sum(coord, vector)]

	free = ([coord1, coord2]) -> diff(coord2, coord1)
	pmult = (pvector=[coord1, _], scalar) -> position(coord1, prod(free(pvector), scalar))
	pdiv = (pvector=[coord1, _], scalar) -> position(coord1, div(free(pvector), scalar))

	constructor: ({@selector}) ->
		@svg = d3.select(@selector)
			.attr('viewBox', "0 0 #{viewBoxWidth} #{viewBoxHeight}")
		d3.json '_static/graph.json', @buildGraph

	buildGraph: (error, @data) =>
		@createDefinitions()
		taskLayout = @createNodes()
		taskLayout.start()

	createDefinitions: () ->
		definitions = @svg.append 'defs'
		arrow = definitions.append('marker')
		arrow.attr('id', 'right-arrowhead')
			.attr('refX', arrowHeight = 4)
			.attr('refY', 	(arrowWidth = 6) / 2)
			.attr('markerWidth', 	arrowHeight)
			.attr('markerHeight', arrowWidth)
			.attr('orient', 'auto')
		  .append('path').attr('d', "M0,0 V#{arrowWidth} L#{arrowHeight},#{arrowWidth/2} Z")

	partitionKey = 'phase'
	nodeColorKey = 'module'

	keyMap:
		phase: 'phases'
		module: 'modules'
	partition: (key, idx) ->
		return @data[@keyMap[key]]

	nodeRadius = 10
	nodePadding = 10
	createNodes: () ->
		options =
			gravity:      0
			linkDistance: 50
			linkStrength: .8
			charge:       -130
			size:         [viewBoxWidth, viewBoxHeight]

		layout = d3.layout.force()
		layout[option](value) for option, value of options

		array_sum = (list) -> list.reduce(((a,b) -> a + b), 0)
		partitioning =
			nonLinear: (groupCounts, range, k=2) ->
				ratios = (Math.pow(count, 1/k) for count in groupCounts)
				fraction = range / (array_sum ratios)
				return (fraction * ratio for ratio in ratios)
			linear: (groups, range) ->
				fraction = range / groups
				return (fraction for _ in [0..groups])
			offset: (ranges, i) -> (array_sum ranges.slice 0, i) + ranges[i] / 2

		layout.nodes @data.nodes
		layout.links @data.links

		grouping = d3.nest().key((d) -> d[partitionKey]).sortKeys(d3.ascending)

		widths = partitioning.nonLinear((d.values for d in grouping.rollup((d) -> d.length).entries(@data.nodes)),
		                                viewBoxWidth - margins.left - margins.right)
		heights = partitioning.nonLinear((d.values for d in grouping.rollup((d) -> d.length).entries(@data.nodes)),
		                                 viewBoxHeight - margins.top - margins.bottom, 4)
		for node in @data.nodes
			# node.cx = margins.left + partitioning.offset(widths, node[partitionKey])
			# node.cy = viewBoxHeight / 2 + margins.top
			node.cx = viewBoxWidth / 2 + margins.left
			node.cy = margins.top + partitioning.offset(heights, node[partitionKey])
			node.radius = nodeRadius


		groups = d3.nest().key((d) -> d[partitionKey])
		                  .sortKeys(d3.ascending)
		                  .entries(layout.nodes())

		hullColors = d3.scale.category20()
		nodeColors = d3.scale.category20c()

		hulls = @svg.append('g').attr('class', 'hulls')
		            .selectAll('path').data(groups).enter()
		            .append('path').attr('id', (d) -> "hull-#{d.key}")
		                           .style
		                             'fill': (d, i) -> hullColors(i)
		                             'stroke': (d, i) -> hullColors(i)
		
		hullLabels = @svg.append('g').attr('class', 'hull-labels')
		                 .selectAll('text').data(groups).enter()
		                 .append('text')
		hullLabels.append('textPath').attr('xlink:href', (d) -> "#hull-#{d.key}")
		                             .text((d) => @partition(partitionKey)[d.key].name)

		links = @svg.append('g').attr('class', 'links')
		            .selectAll('line').data(layout.links()).enter()
		            .append('line').attr('marker-end', 'url(#right-arrowhead)')

		nodes = @svg.append('g').attr('class', 'nodes')
		            .selectAll('g.partition').data(groups).enter()
		            .append('g').attr('class', 'partition')
		            .selectAll('circle').data((d) -> d.values).enter()
		            .append('circle').attr('r', (d) -> d.radius)
		                             .style('fill', (d, i) -> nodeColors(d[nodeColorKey]))
		                             .call(layout.drag)
		                             .on('mouseover', (d) -> (labels.filter (l) -> d is l).classed 'hover', true)
		                             .on('mouseout', (d) -> (labels.filter (l) -> d is l).classed 'hover', false)

		labels = @svg.append('g').attr('class', 'node-labels')
		             .selectAll('g.partition').data(groups).enter()
		             .append('g').attr('class', 'partition')
		             .selectAll('text').data((d) -> d.values).enter()
		             .append('text').text((d) -> d.name)
		                            .attr('transform', (d) -> offset=-(d.radius + 5); "translate(0,#{offset})")

		rotate = (x, n) ->
			n = n % x.length
			x.slice(0,-n).reverse().concat(x.slice(-n).reverse()).reverse()
		circle_coords = (parts) ->
			partSize = 2*Math.PI/parts
			return (for i in [0..parts]
			        theta = partSize*i
			        [(Math.cos theta), (Math.sin theta)])
		hullPointMatrix = (prod(v, nodeRadius*2) for v in circle_coords(16))
		hullBoundaries = (d) ->
			nodePoints = d.values.map (i) -> [i.x, i.y]
			padded_points = []
			padded_points.push sum(p, v) for v in hullPointMatrix for p in nodePoints
			points = d3.geom.hull(padded_points)
			points = rotate points, Math.floor -points.length / 2.5
			"M#{points.join('L')}Z"

		gravity_fn = (alpha) =>
			(d) ->
				d.x += (d.cx - d.x) * alpha * gravity.lateral
				d.y += (d.cy - d.y) * alpha * gravity.longitudinal

		layout.on 'tick', (e) =>
			hulls.attr('d', hullBoundaries)
			nodes.each gravity_fn(e.alpha)
			nodes.attr
				cx: ({x}) -> x
				cy: ({y}) -> y
			labels.each gravity_fn(e.alpha)
			labels.attr
				x: ({x}) -> x
				y: ({y}) -> y
			links.each ({source:{x:x1,y:y1},target:{x:x2,y:y2}}, i) ->
				[x,y] = scale(free([[x1,y1], [x2,y2]]), nodeRadius)
				@setAttribute 'x1', x1 + x
				@setAttribute 'y1', y1 + y
				@setAttribute 'x2', x2 - x
				@setAttribute 'y2', y2 - y

		return layout
