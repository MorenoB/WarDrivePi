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
        private const string NpgsqlConnectionString = "Server=localhost;" +
                                                      "Port=5432;" +
                                                      "Username=postgres;" +
                                                      "Password=g4Kzri^akWWP^LEQ0&Z%QRfW;" +
                                                      "Database=packets;";

        public ActionResult Dashboard()
        {
            return View();
        }

        public ActionResult Map()
        {
            var baseTable = new DataTable();

            using (var npgsqlConnection = new NpgsqlConnection(NpgsqlConnectionString))
            using (var npgsqlCommand = new NpgsqlCommand(Marker.BaseQuery, npgsqlConnection))
            {
                npgsqlConnection.Open();

                using (var npgsqlDataReader = npgsqlCommand.ExecuteReader())
                {
                    baseTable.Load(npgsqlDataReader);
                }

                npgsqlConnection.Close();
            }

            var markers = new ArrayList();
            foreach (DataRow baseTableRow in baseTable.Rows)
            {
                var elementsTable = new DataTable();

                using (var npgsqlConnection = new NpgsqlConnection(NpgsqlConnectionString))
                using (var npgsqlCommand = new NpgsqlCommand(Marker.ElementsQuery, npgsqlConnection))
                {
                    npgsqlConnection.Open();

                    npgsqlCommand.Parameters.AddWithValue("pointer", NpgsqlDbType.Bigint, (long)baseTableRow.ItemArray[0]);
                    npgsqlCommand.Prepare();

                    using (var npgsqlDataReader = npgsqlCommand.ExecuteReader())
                    {
                        elementsTable.Load(npgsqlDataReader);
                    }

                    npgsqlConnection.Close();
                }

                markers.Add(new Marker(baseTableRow, elementsTable));
            }

            foreach (var marker in markers)
            {
                
            }

            return View(markers);
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