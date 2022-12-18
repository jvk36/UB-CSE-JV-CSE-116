function redirect(unitTest=false) {
	localStorage.setItem("name", document.getElementById("name").value);
	localStorage.setItem("unitTest", unitTest);
	if (unitTest) {
		window.location.href="WebApp/game.html";
	} else {
		window.location.href="game.html"
	}
}
