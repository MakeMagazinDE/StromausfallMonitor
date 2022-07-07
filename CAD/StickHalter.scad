//OpenSCAD-Skript

//Moduldefinition mit Parametern
module edge (
//Parameter
hght=5,thck=2.0,rh=6,
lngth1=50, lngth2=75,d1=1.3)
//Beginn Modul
{
difference(){   //difference 1
union(){        //union 1
difference(){   //difference 2
union(){        //union 2
    //alles, was vor der nächsten geschweiften Klammer steht, wird zusammengefügt (union 2)
//Traverse unten
translate([-lngth1,0,0])
cube([lngth1,10,thck]);
//Rippe Traverse
translate([-lngth1,0,0])
cube([lngth1,thck,rh]);
//Stütze hinten
translate([-lngth1,-hght,0])
cube([hght,hght,thck]);
//Rippe Stütze hinten
translate([-lngth1,-hght,0])
cube([thck,hght+10,rh]);
//Vertikale Stütze
translate([-10,0,0])
cube([10,lngth2,thck]); 
//Rippe Vertikale Stütze
translate([-thck,0,0])
cube([thck,lngth2,rh]);     
//translate([0, 0, 0])
//cylinder(d=diaA, h=hght, $fn=32);
//Klotz für Schraube
translate([-10,0,0])
cube([8,12,8]);
//Schräge Rippe
translate([-lngth1,10,0])
rotate([0,0,-31.6])
cube([thck,78.5,rh]);
//Ausleger
translate([-10,lngth2,0])
cube([lngth2+10,10,thck]);
//Rippe Ausleger
translate([-10,lngth2,0])
cube([lngth2+10,thck,rh]);
//Stickträgerprofil
translate([lngth2,18+7,0])
cube([3.3,lngth2-18,3]);
}               //union 2 end
    //alles, was vor der nächsten geschweiften Klammer steht, wird davon abgezogen (difference 2)
translate([-5, -0.1, 4])
rotate([-90,0,0])
cylinder(d=3.3, h=24, $fn=8);
////Stickträgerrinne
translate([lngth2+1,18+3,1.5])
cube([1.5,lngth2-18,3]);

}  //difference 2 end
    //alles, was vor der nächsten geschweiften Klammer steht, wird dazu hinzugefügt (union 1)
//Text


}               //union 1 end
    //alles, was vor der nächsten geschweiften Klammer steht, wird davon wieder abgezogen (difference 1)

}               //difference 1 end

}  //module end


//Hier werden Instanzen des Moduls aufgerufen
 

translate([0,0,0]) edge();
rotate([0,0,180])
translate([-22,-68,0]) edge();
