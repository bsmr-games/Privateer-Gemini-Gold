uniform int light_enabled[gl_MaxLights];
uniform int max_light_enabled;
uniform sampler2D diffuseMap;
uniform sampler2D envMap;
uniform sampler2D specMap;
uniform sampler2D glowMap;
uniform sampler2D normalMap;
uniform sampler2D damageMap;
uniform sampler2D detail0Map;
uniform sampler2D detail1Map;
uniform vec4 cloaking;
uniform vec4 damage;
//varying vec4 gl_FrontColor;
vec3 matmul(vec3 tangent, vec3 binormal, vec3 normal,vec3 lightVec) {
  return vec3(dot(lightVec,tangent),dot(lightVec,binormal),dot(lightVec,normal));
}
vec3 imatmul(vec3 tangent, vec3 binormal, vec3 normal,vec3 lightVec) {
  return lightVec.xxx*tangent+lightVec.yyy*binormal+lightVec.zzz*normal;
}

vec3 expand(vec3 expandme) {
  //debug only--if you dont want to use bump mapreturn vec3(0,0,1);
  return expandme*vec3(2.0)-vec3(1.0);
}
vec2 EnvMapGen(vec3 f) {
   float fzp1=f.z+1.0;
   float m=2.0*sqrt(f.x*f.x+f.y*f.y+(fzp1)*(fzp1));
   return vec2(f.x/m+.5,f.y/m+.5);
}

void main() {
  //begin bumpmapping
  vec3 iNormal=gl_TexCoord[1].xyz;
  vec3 iTangent=gl_TexCoord[2].xyz;
  vec3 iBinormal=gl_TexCoord[3].xyz;
//download matrix and dont recompute (as below you might... slightly higher precision, no visual diff)
  //iBinormal=normalize(cross(iNormal,iTangent));
  //iTangent=normalize(cross(iBinormal,iNormal));

  vec3 iEyeDir=gl_TexCoord[4].xyz;
  vec3 light0Dir=gl_TexCoord[5].xyz;
  vec3 eyeDir=iEyeDir;//eyeDir=normalize(matmul(iTangent,iBinormal,iNormal,iEyeDir));
//keep everything in world space
  vec3 half0Angle=normalize(eyeDir+light0Dir);
  vec3 normal;//=normalize(expand(texture2D(normalMap,gl_TexCoord[0].xy).wyz));
//transform normal from normalMap to world space
  normal=normalize(imatmul(iTangent,iBinormal,iNormal,expand(texture2D(normalMap,gl_TexCoord[0].xy).wyz)));
  //begin shading
//compute half angle dot with light (not used)
  float nDotH0=dot(normal,half0Angle);
//compute normal dot with light
  float nDotL0=dot(normal,light0Dir);
//compute eye direction reflected across normal
  vec3 reflection=reflect(-eyeDir,normal);
//compute dot light dir and reflected vector
  float lDotR0=dot(light0Dir,reflection);
//get damaged and undamaged colors
  vec4 undamagedcolor=texture2D(diffuseMap,gl_TexCoord[0].xy);
  vec4 damagecolor=texture2D(damageMap,gl_TexCoord[0].xy);
//mix the colors based on damage... if you had detail maps, these would go here
  vec4 diffsurface=
	mix(undamagedcolor,damagecolor,damage.x);
	//	+texture2D(detail0Map,gl_TexCoord[7].xy);//do not support yet
//have a specular surface unless the damage color is quite bright (maybe dark!?)
  vec4 specsurface=texture2D(specMap,gl_TexCoord[0].xy)*(1.0-damagecolor*damage.x*2.0);
//add in lights 1..8 and ambient terms
  vec4 ambient=gl_Color;
  vec4 att0=vec4(gl_TexCoord[5].w);
  ambient+=max(nDotL0,0.0)*gl_FrontLightProduct[0].diffuse/att0;
//find the color of specularity of this surface... lookup in env map the normal
  vec4 specularity=gl_SecondaryColor+texture2D(envMap,EnvMapGen(reflection));
//add in the lDotR product
 specularity+=pow(max(lDotR0,0.0),gl_FrontMaterial.shininess)*gl_FrontLightProduct[0].specular/att0;
  if (light_enabled[1]!=0) {
    //add in the dot of light and normal* diffuse mat*diffuse light
    vec3 light1Dir=gl_TexCoord[6].xyz;
    vec3 half1Angle=normalize(eyeDir+light1Dir);
    float nDotH1=dot(normal,half1Angle);
    float nDotL1=dot(normal,light1Dir);
    float lDotR1=dot(light1Dir,reflection);
    vec4 att1=vec4(gl_TexCoord[6].w);
    ambient+=max(nDotL1,0.0)*gl_FrontLightProduct[1].diffuse/att1;
    specularity+=pow(max(lDotR1,0.0),gl_FrontMaterial.shininess)*gl_FrontLightProduct[1].specular/att1;
  }
//sum everything up including glow from surface...and if cloaking, fade it out :-)
  gl_FragColor=(ambient*diffsurface+specularity*specsurface+texture2D(glowMap,gl_TexCoord[0].xy))*cloaking.rrrg;
}