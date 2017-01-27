using System.Web;
using System.Web.Optimization;

namespace WarDrivePiServer
{
    public class BundleConfig
    {
        // For more information on bundling, visit http://go.microsoft.com/fwlink/?LinkId=301862
        public static void RegisterBundles(BundleCollection bundles)
        {
            bundles.Add(new ScriptBundle("~/bundles/sb-admin-2-js").Include(
                "~/Scripts/jquery.min.js",
                "~/Scripts/bootstrap.min.js",
                "~/Scripts/metisMenu.min.js",
                "~/Scripts/sb-admin-2.min.js",
                "~/Scripts/extensions.js"
                ));

            bundles.Add(new StyleBundle("~/Content/sb-admin-2-css").Include(
                "~/Content/bootstrap.min.css",
                "~/Content/metisMenu.min.css",
                "~/Content/sb-admin-2.min.css",
                "~/Content/font-awesome.min.css",
                "~/Content/site.css"));

            bundles.Add(new ScriptBundle("~/bundles/Map").Include(
                "~/Scripts/leaflet.js",
                "~/Scripts/leaflet.markercluster.js",
                "~/Scripts/Map.js"));

            bundles.Add(new StyleBundle("~/Content/Map").Include(
                "~/Content/leaflet.css",
                "~/Content/MarkerCluster.css",
                "~/Content/MarkerCluster.Default.css"));
        }
    }
}
