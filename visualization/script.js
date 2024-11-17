// script.js

// Set the dimensions and margins of the graph
const margin = { top: 50, right: 30, bottom: 70, left: 60 },
      width = 960 - margin.left - margin.right,
      height = 600 - margin.top - margin.bottom;

// Append the SVG object to the div with id "chart"
const svg = d3.select("#chart")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

// Tooltip setup
const tooltip = d3.select("body")
    .append("div")
    .attr("id", "tooltip")
    .style("position", "absolute")
    .style("visibility", "hidden")
    .style("background-color", "rgba(0, 0, 0, 0.8)")
    .style("color", "white")
    .style("padding", "8px")
    .style("border-radius", "4px")
    .style("font-size", "12px")
    .style("pointer-events", "none");

// Load the CSV data
d3.csv("combined_betting_data.csv").then(function(data) {
    // Convert string numbers to actual numbers
    data.forEach(d => {
        d["Average Home Win Probability"] = +d["Average Home Win Probability"];
        d["Average Draw Probability"] = +d["Average Draw Probability"];
        d["Average Away Win Probability"] = +d["Average Away Win Probability"];
        d["Average Home Win Odds"] = +d["Average Home Win Odds"];
        d["Average Draw Odds"] = +d["Average Draw Odds"];
        d["Average Away Win Odds"] = +d["Average Away Win Odds"];
    });

    // Define subgroups and groups
    const subgroups = ["Average Home Win Probability", "Average Draw Probability", "Average Away Win Probability"];
    const groups = data.map(d => `${d["Home Team"]} vs ${d["Away Team"]}`);

    // Scales
    const x = d3.scaleBand()
        .domain(groups)
        .range([0, width])
        .padding(0.2);

    const xSubgroup = d3.scaleBand()
        .domain(subgroups)
        .range([0, x.bandwidth()])
        .padding(0.05);

    const y = d3.scaleLinear()
        .domain([0, 100]) // Probabilities are percentages
        .nice()
        .range([height, 0]);

    const color = d3.scaleOrdinal()
        .domain(subgroups)
        .range(['#1f77b4', '#ff7f0e', '#2ca02c']);

    // Axes
    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).tickSize(0))
        .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");

    svg.append("g")
        .call(d3.axisLeft(y));

    // Bars with tooltip functionality
    svg.append("g")
        .selectAll("g")
        .data(data)
        .join("g")
            .attr("transform", d => `translate(${x(`${d["Home Team"]} vs ${d["Away Team"]}`)}, 0)`)
        .selectAll("rect")
        .data(d => subgroups.map(key => ({
            key: key,
            value: d[key],
            team: `${d["Home Team"]} vs ${d["Away Team"]}`,
            avgOdds: key === "Average Home Win Probability" ? d["Average Home Win Odds"] :
                     key === "Average Draw Probability" ? d["Average Draw Odds"] : d["Average Away Win Odds"]
        })))
        .join("rect")
            .attr("x", d => xSubgroup(d.key))
            .attr("y", d => y(d.value))
            .attr("width", xSubgroup.bandwidth())
            .attr("height", d => height - y(d.value))
            .attr("fill", d => color(d.key))
            .on("mouseover", (event, d) => {
                tooltip.style("visibility", "visible")
                       .html(`
                           <strong>Match:</strong> ${d.team}<br>
                           <strong>Category:</strong> ${d.key.replace('Average ', '').replace(' Probability', '')}<br>
                           <strong>Probability:</strong> ${d.value.toFixed(2)}%<br>
                           <strong>Odds:</strong> ${d.avgOdds.toFixed(2)}
                       `);
            })
            .on("mousemove", (event) => {
                tooltip.style("top", `${event.pageY + 10}px`)
                       .style("left", `${event.pageX + 10}px`);
            })
            .on("mouseout", () => {
                tooltip.style("visibility", "hidden");
            });

    // Legend
    const legend = svg.selectAll(".legend")
        .data(subgroups)
        .enter().append("g")
            .attr("transform", (d, i) => `translate(0,${i * 20})`);

    legend.append("rect")
        .attr("x", width - 18)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", d => color(d));

    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(d => d.replace('Average ', '').replace(' Probability', ''));
});