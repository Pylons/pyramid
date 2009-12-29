TEXDIR=.build/latex

for img in $TEXDIR/*.png;
do
    cp $img ${img}.BAK
    convert $img -units PixelsPerInch -resample 300 -colorspace Gray ${img}.grey
    mv ${img}.grey $img
done

