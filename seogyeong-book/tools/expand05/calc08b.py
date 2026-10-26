from lib import *
tx,ty=ll2xy(TLAT,TLON)
# 올바른 값
d_ok=math.hypot(tx,ty); b_ok=brg(tx,ty)
# 함정1: 경도 1도를 111.2 km로 (위도에 따른 감소를 잊음)
tx1=(TLON-LON0)*KLAT; d1=math.hypot(tx1,ty); b1=brg(tx1,ty)
# 함정2: 도분초를 십진수 도로 잘못 읽음 (39°04'26" -> 39.0426)
lat_bad=39.0426; lon_bad=125.4942
ty2=(lat_bad-LAT0)*KLAT; tx2=(lon_bad-LON0)*KLON
d2=math.hypot(tx2,ty2); b2=brg(tx2,ty2)
dlat_err=(lat_bad-TLAT)*KLAT
# 함정3: 경도 환산 오류가 '동쪽 7.2 km' 끝점에 주는 경도 차이
lon_ok=7.2/KLON; lon_bad3=7.2/KLAT
diff_deg=lon_ok-lon_bad3; diff_km=diff_deg*KLON
# 방위 판정이 바뀌는가: 평양 점에서 대성산이 북동 부채꼴(22.5~67.5)인가
in_ne_ok=22.5<=b_ok<=67.5; in_ne_1=22.5<=b1<=67.5
# 함정4: 위도와 경도를 바꿔 씀
sw_x=(TLAT-LON0)*KLON; 
if __name__=="__main__":
    print(tx,ty,d_ok,b_ok); print(tx1,d1,b1); print(tx2,ty2,d2,b2,dlat_err); print(lon_ok,lon_bad3,diff_deg,diff_km)
