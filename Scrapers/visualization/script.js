// script.js

// Load the CSV data
d3.csv("most_profitable_matches.csv").then(function(data) {
    // Dynamically infer the columns from the CSV
    const columns = Object.keys(data[0]); // Get the column names from the first row of the CSV

    // Create the table structure
    const table = d3.select("body").append("table");
    const thead = table.append("thead");
    const tbody = table.append("tbody");

    // Append the header row
    thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
        .text(d => d);

    // Append the rows
    const rows = tbody.selectAll("tr")
        .data(data)
        .enter()
        .append("tr")
        // Add highlighting logic based on a column
        .attr("class", d => +d["Expected Value"] > 1 ? "highlight" : "");

    // Append the cells
    rows.selectAll("td")
        .data(d => columns.map(column => d[column]))
        .enter()
        .append("td")
        .text(d => d);
});
