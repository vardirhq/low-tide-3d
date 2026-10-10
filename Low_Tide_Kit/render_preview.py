"""Render actual kit triangles with a small orthographic CPU rasterizer."""
from build_kit import *
from PIL import Image,ImageDraw,ImageFont,ImageFilter
def world(instances):
 out=[]
 for a in instances:
  t=math.radians(a['yaw_degrees']);c,s=math.cos(t),math.sin(t);R=np.array([[c,-s,0],[s,c,0],[0,0,1]])
  for p in K[a['asset']]['parts']:
   out.append(((p['v']@R.T+a['position'])[p['f']],p['mat']))
 return out
def render(instances,path,w=1500,h=1250,eye=(8,-11,11),scale=105,target=(0,-.6,1.2),light=(-3,-4,8)):
 geom=world(instances);eye=np.array(eye,float);eye/=np.linalg.norm(eye);right=np.cross([0,0,1],eye);right/=np.linalg.norm(right);up=np.cross(eye,right);basis=np.array([right,up,eye]);target=np.array(target,float)
 bg=np.array([34,45,49],float);rgb=np.zeros((h,w,3))+bg;depth=np.full((h,w),-1e10)
 light=np.array(light,float);light/=np.linalg.norm(light)
 def drawtri(tri,color):
  q=(tri-target)@basis.T;q[:,:2]*=scale;q[:,0]+=w/2;q[:,1]=h/2-q[:,1]
  x0=max(0,int(np.floor(q[:,0].min())));x1=min(w-1,int(np.ceil(q[:,0].max())));y0=max(0,int(np.floor(q[:,1].min())));y1=min(h-1,int(np.ceil(q[:,1].max())))
  if x1<x0 or y1<y0:return
  a,b,c=q;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-8:return
  xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
  u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;zz=u*a[2]+v*b[2]+(1-u-v)*c[2]
  sub=depth[y0:y1+1,x0:x1+1];mask=(u>=-1e-6)&(v>=-1e-6)&(u+v<=1.000001)&(zz>sub)
  sub[mask]=zz[mask];rgb[y0:y1+1,x0:x1+1][mask]=color
 # Ground and cast shadow, formed from actual mesh silhouettes.
 ground=np.array([[-200,-200,-.04],[200,-200,-.04],[200,200,-.04],[-200,200,-.04]])
 for f in [[0,1,2],[0,2,3]]:drawtri(ground[f],[42,54,57])
 for tris,mat in geom:
  for tri in tris:
   shadow=tri.copy();shadow[:,:2]-=(shadow[:,2:3]+.03)*light[:2]/light[2];shadow[:,2]=-.03;drawtri(shadow,[27,36,39])
 for tris,mat in geom:
  col=np.array([int(M[mat][0][i:i+2],16) for i in (1,3,5)])
  for tri in tris:
   n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);ln=np.linalg.norm(n)
   if ln<1e-9:continue
   n/=ln
   if np.dot(n,eye)<=0:continue
   shade=.46+.46*max(0,np.dot(n,light))+.13*max(0,n[2]);color=np.clip(col*shade,0,255)
   if mat=='lamp':color=col
   drawtri(tri,color)
 Image.fromarray(rgb.astype('uint8')).save(path)
if __name__=='__main__':
 render([a for a in A if a['group'] not in ['roof','upper_walls']],P/'preview_cutaway.png')
 render(A,P/'preview_exterior.png',eye=(8,11,9))
 print('Rendered cutaway and exterior from exported-source geometry.')
