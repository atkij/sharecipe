(function() {
	function requestWakeLock() {
		if ('WakeLock' in window && 'request' in window.WakeLock) {
			console.log('window wakelock');
			let wakeLock = null;

			const request = () => {
				const controller = new AbortController();
				const signal = controller.signal;
				
				window.WakeLock.request('screen', {signal})
				.catch((e) => {
					if (e.name === 'AbortError') {
						requestWakeLock();
					}
				});
			};

			request();

		} else if ('wakeLock' in navigator && 'request' in navigator.wakeLock) {
			console.log('navigator wakelock');
			let wakeLock = null;

			const request = async () => {
				try {
					wakeLock = await navigator.wakeLock.request('screen');
					wakeLock.addEventListener('release', (e) => {
						console.log('release callback');
						requestWakeLock();
					});
				} catch(e) {}
			};

			request();
		}
	}
	
	addEventListener("focus", (e) => {
		requestWakeLock();
	});

	requestWakeLock();
})();
