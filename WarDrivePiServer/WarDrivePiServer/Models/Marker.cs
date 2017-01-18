using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Web;

namespace WarDrivePiServer.Models
{
    public class Marker
    {
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
            WHERE pointer_dot11 = @pointer;";

        private readonly DataRow _baseTableRow;
        private readonly DataTable _elementsTable;

        public Marker(DataRow baseTableRow, DataTable elementsTable)
        {
            _baseTableRow = baseTableRow;
            _elementsTable = elementsTable;
        }
    }
}