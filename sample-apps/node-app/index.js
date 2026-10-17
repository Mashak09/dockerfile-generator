const express = require("express");

const app = express();
const PORT = 3000;

app.get("/", (req, res) => {
  res.send("Hello from the Node sample app\n");
});

app.listen(PORT, "0.0.0.0", () => {
  console.log("Listening on port " + PORT);
});
