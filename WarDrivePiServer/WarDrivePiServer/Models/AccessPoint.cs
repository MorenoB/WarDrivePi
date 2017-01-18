using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Text;
using System.Text.RegularExpressions;
using System.Web;
using System.Web.Script.Serialization;
using System.Xml.Serialization;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace WarDrivePiServer.Models
{
    public class AccessPoint
    {

        public enum WirelessSecurity
        {
            Open,
            WiredEquivalentPrivacy,
            WiFiProtectedAccess,
            WiFiProtectedAccess2
        }

        public enum WirelessCapability
        {
            // Currently supported are:
            EssCapabilities = 1,    // First bit
            Privacy = 5             // Fifth bit
        }

        public const string BaseQuery =
            @"SELECT *
            FROM dot11
            JOIN dot11_beacon USING(pointer_dot11)
            --JOIN dot11_elt USING(pointer_dot11)
            LEFT JOIN LATERAL (
                SELECT *
                FROM sensor_gps
                ORDER BY ABS(
                    DATE_PART('day', sensor_gps.timestamp - dot11_beacon.timestamp) * 24 * 60 * 60
                    + DATE_PART('hour', sensor_gps.timestamp - dot11_beacon.timestamp) * 60 * 60
                    + DATE_PART('minute', sensor_gps.timestamp - dot11_beacon.timestamp) * 60
                    + DATE_PART('second', sensor_gps.timestamp - dot11_beacon.timestamp)
                ) ASC LIMIT 1
            ) AS sensor_gps_lateral ON TRUE;";

        public const string ElementsQuery =
            @"SELECT *
            FROM dot11_elt
            WHERE pointer_dot11 = @pointer_dot11;";

        private readonly DataRow _baseDataRow;
        private readonly DataTable _elementsDataTable;

        [JsonIgnore]
        public PhysicalAddress BssId { get; private set; }
        [JsonProperty(PropertyName = "BssId")]
        public string BssIdString
        {
            get { return BssId.ToString(); }
            private set { BssId = string.IsNullOrEmpty(value) || string.IsNullOrWhiteSpace(value) ? PhysicalAddress.None : PhysicalAddress.Parse(value); }
        }

        [JsonIgnore]
        public PhysicalAddress TransmitterAddress { get; private set; }
        [JsonProperty(PropertyName = "TransmitterAddress")]
        public string TransmitterAddressString
        {
            get { return TransmitterAddress.ToString(); }
            private set { TransmitterAddress = string.IsNullOrEmpty(value) || string.IsNullOrWhiteSpace(value) ? PhysicalAddress.None : PhysicalAddress.Parse(value); }
        }

        public bool TransmitterIsAccessPoint { get; private set; }
        public string Ssid { get; private set; }
        public int Channel { get; private set; }
        public WirelessSecurity Security { get; private set; }
        public int BeaconInterval { get; private set; }
        public Coordinates Coordinates { get; private set; }


        public AccessPoint(DataRow baseDataRow, DataTable elementsDataTable)
        {
            _baseDataRow = baseDataRow;
            _elementsDataTable = elementsDataTable;
        }

        public void Process()
        {
            ProcessElements();
            ProcessBase();
        }

        private void ProcessBase()
        {
            BssId = (PhysicalAddress)RowValueByColumnName(_baseDataRow, "address3");
            TransmitterAddress = (PhysicalAddress)RowValueByColumnName(_baseDataRow, "address2");
            BeaconInterval = (int)RowValueByColumnName(_baseDataRow, "beacon_interval");

            // Use capablity information
            var capabilities = (BitArray)RowValueByColumnName(_baseDataRow, "capabilities_information");

            TransmitterIsAccessPoint = capabilities[capabilities.Length - (int)WirelessCapability.EssCapabilities];

            if (Security == WirelessSecurity.Open && capabilities[capabilities.Length - (int)WirelessCapability.Privacy])
                Security = WirelessSecurity.WiredEquivalentPrivacy;

            // Use GPS information
            Coordinates = new Coordinates
            {
                Latitude = (double)RowValueByColumnName(_baseDataRow, "latitude"),
                Longitude = (double)RowValueByColumnName(_baseDataRow, "longitude"),
                Altitude = (double)RowValueByColumnName(_baseDataRow, "altitude"),
                Accuracy = (double)RowValueByColumnName(_baseDataRow, "accuracy")
            };
        }

        private void ProcessElements()
        {
            var infoQuotes = new[] { "\"", "'" };

            foreach (DataRow elementsDataRow in _elementsDataTable.Rows)
            {
                var number = (short)RowValueByColumnName(elementsDataRow, "number");
                var info = (string)RowValueByColumnName(elementsDataRow, "info");

                // Remove begin and end quotes
                foreach (var infoQuote in infoQuotes)
                    if (info.StartsWith(infoQuote) && info.EndsWith(infoQuote))
                        info = info.Substring(1, info.Length - 2);

                switch (number)
                {
                    case 0:
                        Ssid = info;
                        break;

                    case 3:
                        Channel = Encoding.UTF8.GetBytes(Regex.Unescape(info))[0];
                        break;

                    case 48:
                        Security = WirelessSecurity.WiFiProtectedAccess2;
                        break;

                    case 221:
                        Security = info.StartsWith("\\x00P\\xf2\\x01\\x01\\x00")
                            ? WirelessSecurity.WiFiProtectedAccess
                            : Security;
                        break;

                    default:
                        break;
                }
            }
        }

        private object RowValueByColumnName(DataRow dataRow, string columnName)
        {
            return dataRow[dataRow.Table.Columns[columnName].Ordinal];
        }
    }

    public class Coordinates
    {
        public double Latitude, Longitude, Altitude, Accuracy;
    }
}