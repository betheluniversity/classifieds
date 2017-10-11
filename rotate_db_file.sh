DATEVAR=`date "+%m-%d-%Y_%H:%M%p"`
sqlite3 /opt/<directory>/classifieds/app.db .dump > /opt/<directory>/db_back/app.db.bak_$DATEVAR
find /opt/<directory>/db_back/app.db.bak* -mtime +13 -type f -exec rm {} \;

// Copy those 3 lines to /opt/<directory/rotate_db_file.sh, and replace <directory> with the actual folder name
// (like classifieds and book_exchange)

// Finally, here's the cronjob used to run it every 6 hours:
0 */6 * * * /opt/<directory>/rotate_db_file.sh