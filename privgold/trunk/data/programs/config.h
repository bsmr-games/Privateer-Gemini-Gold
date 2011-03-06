/**********************************/
//  CUSTOMIZATION  (EDITABLE)
/**********************************/
#define DEGAMMA              1
#define DEGAMMA_SPECULAR     1
#define DEGAMMA_GLOW_MAP     1
#define DEGAMMA_LIGHTS       1
#define DEGAMMA_ENVIRONMENT  1
#define DEGAMMA_TEXTURES     1
/**********************************/

//      CONSTANTS
#define TWO_PI     (6.2831853071795862)
#define HALF_PI    (1.5707963267948966)
#define PI_OVER_3  (1.0471975511965976)



/**********************************/
//  SELF-ADAPTATION DEFINES
//  (externally controlled)
/**********************************/

#ifndef SRGB_FRAMEBUFFER
#define SRGB_FRAMEBUFFER 0
#endif

#if (SRGB_FRAMEBUFFER != 0)
#define REGAMMA 0
#else
#define REGAMMA 1
#endif

