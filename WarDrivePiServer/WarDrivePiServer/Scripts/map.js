function Map() {
    //-- CLASSES
    var TemplateIcon = L.Icon.extend({
        options: {
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -19]
        }
    });

    //-- GLOBAL VARIABLES
    var defaultZoom = 16;
    var templateIconUrls = {
        User: "../Content/Images/gps-dot.png",
        ApOpen: "../Content/Images/wifi-signal-with-exclamation-mark.png",
        ApWep: "../Content/Images/protected-wireless-network-1.png",
        ApWpa: "../Content/Images/protected-wireless-network-2.png",
        ApWpa2: "../Content/Images/protected-wireless-network-3.png",
        ApUndefined: "../Content/Images/search-wireless-net.png"
    }

    //-- VARIABLES
    var userMarker;
    var accessPointMarkers;
    var timeout;
    var map;

    //-- CONSTRUCTOR
    map = L.map("map")
        .addLayer(
            L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
                attribution: "The Wardrive Project",
                id: "zgl9hfnzmnet.2khh4b0p",
                accessToken: "pk.eyJ1IjoiemdsOWhmbnptbmV0IiwiYSI6ImNpeHVtaXI3aTAwMzEyeHFxZHYwb2g2ZWEifQ.WzA0GNxS1eNBFI595CPkJg"
            }))
        .on("zoom", function () {
            console.log("getZoom() = " + map.getZoom());
            if (map.getZoom() >= 13) {
                if (userMarker) $(userMarker.icon).show();
            } else {
                if (userMarker) $(userMarker.icon).hide();
            }
        });

    //-- PRIVATE FUNCTIONS
    var showAlert = function (message) {
        $("#dismissable-notifications").append(
            $('<div class="alert alert-danger alert-dismissable">\
                <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>\
                {0}\
            </div>'
        .format(message)));
    }

    var showAccessPoints = function (accessPoints) {

        var markerClusters = L.markerClusterGroup({
            maxClusterRadius: 100,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: false,

            spiderfyDistanceMultiplier: 1.5
        });

        accessPointMarkers = [];
        accessPoints.forEach(function (accessPoint, index, array) {

            var apIcon;
            var apSecNice;
            switch (accessPoint.Security) {
                case "Open":
                    apIcon = new TemplateIcon({ iconUrl: templateIconUrls.ApOpen });
                    apSecNice = "Open";
                    break;

                case "WiredEquivalentPrivacy":
                    apIcon = new TemplateIcon({ iconUrl: templateIconUrls.ApWep });
                    apSecNice = "Wired Equivalent Privacy";
                    break;

                case "WiFiProtectedAccess":
                    apIcon = new TemplateIcon({ iconUrl: templateIconUrls.ApWpa });
                    apSecNice = "Wi-Fi Protected Access";
                    break;

                case "WiFiProtectedAccess2":
                    apIcon = new TemplateIcon({ iconUrl: templateIconUrls.ApWpa2 });
                    apSecNice = "Wi-Fi Protected Access II";
                    break;

                default:
                    apIcon = new TemplateIcon({ iconUrl: templateIconUrls.ApUndefined });
                    apSecNice = "&lt;unknown&gt;";
            };
            
            if (!accessPoint.Vendor) {
                accessPoint.Vendor = "&lt;unknown&gt;";
                /*$.ajax({
                    type: "GET",
                    url: "https://macvendors.co/api/{0}"
                        .format(accessPoint.BssId.match(/.{1,2}/g).join(":")),
                    success: function (result) {
                        console.log(result);
                    },
                    async: false
                });*/
            }

            if (!accessPoint.Location) {
                accessPoint.Location = "&lt;unknown&gt;";
                /*$.ajax({
                    type: "GET",
                    url: "https://nominatim.openstreetmap.org/reverse?format=xml&lat={0}&lon={1}&zoom=18"
                        .format(accessPoint.Coordinates.Longitude, accessPoint.Coordinates.Latitude),
                    success: function (result) {
                        console.log(result);
                    },
                    async: false
                });*/
            }
            
            var apNotes =
                "<b>{0}</b><br\>\
                MAC: {1}<br\>\
                Vendor: {2}<br\>\
                Channel: {3}<br\>\
                Frequency: {4} GHz<br\>\
                Security: {5}<br\>\
                Location: {6}<br\>\
                GPS: {7}, {8}"
                .format(
                    accessPoint.SsId.length > 0 ? accessPoint.SsId : "&lt;hidden&gt;",
                    accessPoint.BssId.match(/.{1,2}/g).join(":"),
                    accessPoint.Vendor,
                    accessPoint.Channel,
                    2.407 + (accessPoint.Channel * 0.005),
                    apSecNice,
                    accessPoint.Location,
                    accessPoint.Coordinates.Latitude, accessPoint.Coordinates.Longitude
                );

            var apMarker = L.marker(
                [accessPoint.Coordinates.Latitude, accessPoint.Coordinates.Longitude], { icon: apIcon })
                .bindPopup(apNotes);

            if (!accessPointMarkers)
                accessPointMarkers.push(apMarker);
            markerClusters.addLayer(apMarker);
        });

        map.addLayer(markerClusters);
    }

    var showGeoLocationError = function (error) {
        var errorMessage;
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
        showAlert(errorMessage);
    }

    var showGeoLocation = function (position) {
        clearTimeout(timeout);

        var userIcon = new TemplateIcon({ iconUrl: templateIconUrls.User });

        userMarker = L.marker([position.coords.latitude, position.coords.longitude], { icon: userIcon })
            .bindPopup("You are here!")
            .addTo(map);

        map.setView([position.coords.latitude, position.coords.longitude], defaultZoom);
        userMarker.openPopup();
    }

    //-- PUBLIC FUNCTIONS
    this.addAccessPoints = function (accessPoints) {
        showAccessPoints(accessPoints);
    }

    this.setGeoLocation = function () {
        if (navigator.geolocation) {
            timeout = setTimeout(function () { showGeoLocationError({ code: 3, TIMEOUT: 3 }); }, 5000);
            navigator.geolocation.getCurrentPosition(showGeoLocation, showGeoLocationError, { enableHighAccuracy: true });
        } else { showGeoLocationError(null); }
    }
}