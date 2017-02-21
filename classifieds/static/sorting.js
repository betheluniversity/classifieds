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
                    sortPrice(".price", true);
                else if ($(".selectSort option:selected").text() == "Price (Low-High)")
                    sortPrice(".price", false);
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

            function sortPrice(sortQuery, reverse) {
                var re = /(\d+(\.?(\d*)))/g;
                jQuery(".table > .singlePost").sort(function (a, b) {
                    var test1 = jQuery('> .row > ' + sortQuery, a).text();
                    var test2 = jQuery('> .row > ' + sortQuery, b).text();
                    var match1 = test2.match(re);
                    var match2 = test1.match(re);
                    var result1, result2;

                    if( match1 == null ){
                        result1 = 0;
                    }
                    else {
                        result1 = parseFloat(match1[0]);
                    }

                    if( match2 == null ){
                        result2 = 0;
                    }
                    else {
                        result2 = parseFloat(match2[0]);
                    }

                    if(result1 > result2 && reverse == true) {
                        return 1;
                    }
                    else if (result1 < result2 && reverse == false) {
                        return 1;
                    }
                    else{
                        return -1;
                    }
                }).appendTo('.table');
            };