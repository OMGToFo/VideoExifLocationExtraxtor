mkdir -p ~/.local/bin
wget https://exiftool.org/Image-ExifTool-12.61.tar.gz
tar -xzf Image-ExifTool-12.61.tar.gz
cd Image-ExifTool-12.61
perl Makefile.PL
make install DESTDIR=~/.local
