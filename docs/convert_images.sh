TEXDIR=_build/latex

if test ! -z $BOOK; then
  for img in $TEXDIR/*.png;
  do
      cp $img ${img}.BAK
      convert $img -units PixelsPerInch -resample 300 -colorspace Gray ${img}.grey
      #convert -strip -density 300 ${img} -units PixelsPerInch -resample 300 -colorspace Gray ${img}.grey
      mv ${img}.grey $img
  done
fi

