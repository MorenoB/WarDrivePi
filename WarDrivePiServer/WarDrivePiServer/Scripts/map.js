function Map() {
    var DefaultZoom = 16
    var UserIcon = L.icon({
        iconUrl: "../Content/Images/gps-dot.png",
        iconSize: [56, 56], // Size of the icon
        iconAnchor: [26, 26], // Point of the icon which will correspond to marker's location
        popupAnchor: [0, -29] // Point from which the popup should open relative to the iconAnchor
    });

    var map = L.map("map")
        .addLayer(
            L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
                attribution: "The Wardrive Project",
                id: "zgl9hfnzmnet.2khh4b0p",
                accessToken: "pk.eyJ1IjoiemdsOWhmbnptbmV0IiwiYSI6ImNpeHVtaXI3aTAwMzEyeHFxZHYwb2g2ZWEifQ.WzA0GNxS1eNBFI595CPkJg"
            }))
        .on("zoom", function () {
            var factor = map.getZoom() - DefaultZoom;
            if (factor > 0) factor = Math.pow(2, factor);
            else if (factor < 0) factor = 1 / Math.pow(2, Math.abs(factor));
            else factor = 1;

            var icon = jQuery.extend(true, {}, UserIcon)

            for (var i = 0; i < 2; i++) {
                icon.options.iconSize[i] *= factor;
                icon.options.iconAnchor[i] *= factor;
                icon.options.popupAnchor[i] *= factor;
            }

            userMarker.setIcon(icon);
            userMarker.update();
        });

    var userMarker;
    var userIcon;

    var timeout;
    this.getLocation = function () {
        if (navigator.geolocation) {
            timeout = setTimeout(function () {
                showError({ code: 3, TIMEOUT: 3 });
            }, 5000);
            navigator.geolocation.getCurrentPosition(showPosition, showError, { enableHighAccuracy: true });
        } else {
            showError(null);

        }
    }

    var showPosition = function (position) {
        clearTimeout(timeout);

        userMarker = L.marker([position.coords.latitude, position.coords.longitude], { icon: UserIcon });
        userMarker.addTo(map);
        map.setView([position.coords.latitude, position.coords.longitude], DefaultZoom);
    }

    var showError = function (error) {
        var errorMessage = "";
        switch (error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = "User denied the request for Geolocation.";
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = "Location information is unavailable.";
                break;
            case error.TIMEOUT:
                errorMessage = "The request to get user location timed out.";
                break;
            case error.UNKNOWN_ERROR:
                errorMessage = "An unknown error occurred.";
                break;
            default:
                errorMessage = "Geolocation is not supported by this browser.";
                break;
        }
        map.setView([0, 0], 0);
        var alertDiv =
            $('<div class="alert alert-danger alert-dismissable">\
                <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>\
                {0}\
            </div>'.format(errorMessage));
        $("body").append(alertDiv);
    }
}