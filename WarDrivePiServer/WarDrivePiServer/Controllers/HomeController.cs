using Npgsql;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using NpgsqlTypes;
using WarDrivePiServer.Models;

namespace WarDrivePiServer.Controllers
{
    public class HomeController : Controller
    {
        private const string NpgsqlConnectionString =
            @"Server=localhost;
            Port=5432;
            Username=postgres;
            Password=g4Kzri^akWWP^LEQ0&Z%QRfW;Database=packets;";

        public ActionResult Dashboard()
        {
            return View();
        }

        public ActionResult Map()
        {
            var baseTable = new DataTable();

            // Select all base information for markers
            using (var npgsqlConnection = new NpgsqlConnection(NpgsqlConnectionString))
            using (var npgsqlCommand = new NpgsqlCommand(AccessPoint.BaseQuery, npgsqlConnection))
            {
                npgsqlConnection.Open();

                using (var npgsqlDataReader = npgsqlCommand.ExecuteReader())
                    baseTable.Load(npgsqlDataReader);


                npgsqlConnection.Close();
            }

            var accessPoints = new List<AccessPoint>();
            foreach (DataRow baseDataRow in baseTable.Rows)
            {
                var elementsDataTable = new DataTable();

                // Select all elements information per marker
                using (var npgsqlConnection = new NpgsqlConnection(NpgsqlConnectionString))
                using (var npgsqlCommand = new NpgsqlCommand(AccessPoint.ElementsQuery, npgsqlConnection))
                {
                    npgsqlConnection.Open();

                    npgsqlCommand.Parameters.AddWithValue("pointer_dot11", NpgsqlDbType.Bigint, (long)baseDataRow.ItemArray[0]);
                    npgsqlCommand.Prepare();

                    using (var npgsqlDataReader = npgsqlCommand.ExecuteReader())
                        elementsDataTable.Load(npgsqlDataReader);

                    npgsqlConnection.Close();
                }

                accessPoints.Add(new AccessPoint(baseDataRow, elementsDataTable));
            }

            accessPoints.ForEach(accessPoint => accessPoint.Process());
            return View(accessPoints);
        }

        public ActionResult Drive()
        {
            return View();
        }

        public ActionResult Database()
        {
            return View();
        }
    }
}