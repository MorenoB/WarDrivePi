using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace WarDrivePiServer.Controllers
{
    public class HomeController : Controller
    {
        public ActionResult Dashboard()
        {
            return View();
        }

        public ActionResult Map()
        {
            return View();
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