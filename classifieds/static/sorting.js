/**
 * Created by tih99924 on 4/15/16.
 * Sorting algorithm for the listings on the homepage and when
 * viewing the user posts
 */

            $(".selectSort").change(function(){
                console.log("inFunction");
                if ($(".selectSort option:selected").text() == "Title (A-Z)")
                    sortPosts(".title > a", true);
                else if ($(".selectSort option:selected").text() == "Title (Z-A)")
                    sortPosts(".title > a", false);
                else if ($(".selectSort option:selected").text() == "Description (A-Z)")
                    sortPosts(".description > article", true);
                else if ($(".selectSort option:selected").text() == "Description (Z-A)")
                    sortPosts(".description > article", false);
                else if ($(".selectSort option:selected").text() == "Price (High-Low)")
                    sortPosts(".price", true);
                else if ($(".selectSort option:selected").text() == "Price (Low-High)")
                    sortPosts(".price", false);
                else if ($(".selectSort option:selected").text() == "Date (Old-New)")
                    sortPosts(".date", true);
                else if ($(".selectSort option:selected").text() == "Date (New-Old)")
                    sortPosts(".date", false);
                else if ($(".selectSort option:selected").text() == "Author (A-Z)")
                    sortPosts(".postedBy > a", true);
                else if ($(".selectSort option:selected").text() == "Author (Z-A)")
                    sortPosts(".postedBy > a", false);
            });

            function sortPosts(sortQuery, reverse) {

                jQuery(".table > .singlePost").sort(function (a, b) {
                    var upA = jQuery('> .row > ' + sortQuery, a).text().toUpperCase();
                    var upB = jQuery('> .row > ' + sortQuery, b).text().toUpperCase();
                    if (upA > upB && reverse == true) {
                        return 1;
                    }
                    else if (upA < upB && reverse == false) {
                        return 1;
                    }
                    else{
                        return -1;
                    }
                }).appendTo('.table');
            };
