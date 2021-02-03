window.addEventListener('beforeunload', (event) => {
    event.preventDefault();
    console.log(window.location)
    // event.returnValue = "Say something here.";
  });
