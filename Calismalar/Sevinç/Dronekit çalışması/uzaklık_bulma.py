
import vincenty


target_locations=((40.2338296,29.0036380),
                  (40.2335511,29.0066528),
                  (40.2339033,29.0094209),
                  (40.2309711,29.0094852),
                  (40.2313560,29.0033484),
                  (40.2325601,29.0042818))


home_konumu=(40.2322488	,29.0070283)

kartezyen_konumlar=[]
for i in target_locations:
    x_icin=(i[0],home_konumu[1])
    y_icin=(home_konumu[0],i[1])

    x_mesafe=vincenty.vincenty(x_icin,home_konumu)
    #Burada eğer konum home konumunun olunda kalıyorsa x_mesafe değerini -1 ile çarp
    if i[0]>home_konumu[0]:
        x_mesafe=x_mesafe*-1000
    else :
        x_mesafe=x_mesafe*1000


    y_mesafe=vincenty.vincenty(y_icin,home_konumu)
    if i[1]>home_konumu[1]:
        y_mesafe=y_mesafe*-1000
    else :
        y_mesafe=y_mesafe*1000

    nokta=(x_mesafe,y_mesafe)
    kartezyen_konumlar.append(nokta)
print(kartezyen_konumlar)




