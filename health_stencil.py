from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel

class LineKernel(StencilKernel):
    """A line stencil that runs over a line of nodes."""
    def kernel(self, inline, outline):
		# lambda1=U(:,2)+c;
		# lambda2=U(:,2)-c;
	    
	    # %Calculate Interface values
	    for i=1:length(k)-1 # -- k(i) is where the junction ends
		# eg. k = 0,2999,5998,8997
	        # %Equations PER ARTERY
	        for n=1:3 # %A,u,p -- HAVE TO CALCULATE all 3 (A,u,p)
				uL(k(i)+i+1:k(i+1)+i,n)= # uL(k(1)+2:k(2)+1,n)= # uL(0+2:2999+1,n) # uL(2:3000,n)
					U(k(i)+1:k(i+1),n)+ # U_j # U(k(1)+1:k(2),n)+ # U(1:2999,n)
					B(k(i)+1:k(i+1),k(i)+1:k(i+1))* # WHERE TO GET THIS? # B(1:2999,1:2999)
					U(k(i)+1:k(i+1),n).* # U_j # U(1:2999,n)
					 (.5*(1-lambda1(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1)))); # (1/2)*(1 - (u+c)_j * dt/dx)
					#(.5*(1-lambda1(1:2999)*delt./delx(1:2999)))
					#(.5*(1-(U(1:2999,2)+c)*delt./delx(1:2999)))
				# uL(2:3000,n) = U(1:2999,n) + B(1:2999,1:2999)*U(1:2999,n).*(.5*(1-(U(1:2999,2)+c)*delt./delx(1:2999)))
				# Do this for each uL:
				# uL(2,n) = U(1,n) + B(1,1)*U(1,n).*(.5*(1-(U(1,2)+c)*delt./delx(1)))
				
				uR(k(i)+i:k(i+1)-1+i,n)= # uR(1:2999,n)
					U(k(i)+1:k(i+1),n)- # U_(j+1) # U(1:2999,n)
					B(k(i)+1:k(i+1),k(i)+1:k(i+1))* # B(1:2999,1:2999)
					U(k(i)+1:k(i+1),n).* # U_(j+1) # U(1:2999,n).
					 (.5*(1+lambda2(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1)))); # (1/2)*(1 - (u-c)_j+1 * dt/dx)
					#(.5*(1+lambda2(1:2999)*delt./delx(1:2999)))
					#(.5*(1+(U(1:2999,2)-c)*delt./delx(1:2999)))
				# uR(1:2999,n) = U(1:2999,n) - B(1:2999,1:2999)*U(1:2999,n).*(.5*(1+(U(1:2999,2)-c)*delt./delx(1:2999)))
				
				# Do this for each uR:
				# uR(1,n) = U(1,n) - B(1,1)*U(1,n).*(.5*(1+(U(1,2)-c)*delt./delx(1)))
			end
	    end	
		
		
	def kernel_interface(self, inline, outline):
		# %Use Euler Equations to coalesce twin edge values
	    # %cstar=sparse(diag((sqrt(E*hstar./(2*rho*Ainitstar)).*uL(:,1).^.25+sqrt(E*hstar./(2*rho*Ainitstar)).*uR(:,1).^.25)/2));
	    # %ORIGINALS
	    uI(:,2)=(1./(2*rho*cstar)).*(uL(:,3)-uR(:,3))+0.5*(uL(:,2)+uR(:,2));
	    uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uL(:,2)-uR(:,2));
	    uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
	
	def kernel_u(self, inline, outline):
		for m=1:length(k)-1
			# A
	        U(k(m)+1:k(m+1),1)=U(k(m)+1:k(m+1),1)+(delt./delx(k(m)+1:k(m+1))).*(uI(k(m)+m:k(m+1)+m-1,1).*uI(k(m)+m:k(m+1)+m-1,2)-uI(k(m)+m+1:k(m+1)+m,1).*uI(k(m)+m+1:k(m+1)+m,2));
		#	U(1:2999,1)=U(1:2999,1)+(delt./delx(1:2999)).*(uI(1:2999,1).*uI(1:2999,2)-uI(2:3000,1).*uI(2:3000,2));
		#	U(1,1)=U(1,1)+(delt./delx(1)).*(uI(1,1).*uI(1,2)-uI(2,1).*uI(2,2));
			# u
	        U(k(m)+1:k(m+1),2)=U(k(m)+1:k(m+1),2)+(delt./delx(k(m)+1:k(m+1))).*(0.5*uI(k(m)+m:k(m+1)+m-1,2).*uI(k(m)+m:k(m+1)+m-1,2)-0.5*uI(k(m)+m+1:k(m+1)+m,2).*uI(k(m)+m+1:k(m+1)+m,2)+uI(k(m)+m:k(m+1)+m-1,3)/rho-uI(k(m)+m+1:k(m+1)+m,3)/rho);
		#	U(1:2999,2)=U(1:2999,2)+(delt./delx(1:2999)).*(0.5*uI(1:2999,2).*uI(1:2999,2)-0.5*uI(2:3000,2).*uI(2:3000,2)+uI(1:2999,3)/rho-uI(2:3000,3)/rho);
		#	U(1,2)=U(1,2)+(delt./delx(1)).*(0.5*uI(1,2).*uI(1,2)-0.5*uI(2,2).*uI(2,2)+uI(1,3)/rho-uI(2,3)/rho);
			# p
	        U(k(m)+1:k(m+1),3)=betas(k(m)+1:k(m+1))./Ainit(k(m)+1:k(m+1)).*(sqrt(U(k(m)+1:k(m+1),1))-sqrt(Ainit(k(m)+1:k(m+1))));
		#	U(1:2999,3)=betas(1:2999)./Ainit(1:2999).*(sqrt(U(1:2999,1))-sqrt(Ainit(1:2999)));
		#	U(1,3)=betas(1)./Ainit(1).*(sqrt(U(1,1))-sqrt(Ainit(1)));
	    end

# from stencil_kernel import *
# from stencil_grid import *
# from numpy import pi	
# class MyKernel(StencilKernel):
# 	def kernel(self, node_tuple_ingrid, edge_interface_outgrid):
# 		for x in edge_interface_outgrid.interior_points():
# 			for y in node_tuple_ingrid.neighbors(x, -1):
# 					edge_interface_outgrid[x] = node_tuple_ingrid[y]
# 
# 
# 
# if __name__ == '__main__':
# 	
# 	kernel = MyKernel()
# 	domain_length = 10
# 	# using 1D grids
# 	uL = StencilGrid([domain_length])
# 	uR = StencilGrid([domain_length])
# 	uI = StencilGrid([domain_length])
# 	
# 	
# 	# fill in_grid interior points with ones	
# 	for x in in_grid.interior_points():
# 		print x
# 		in_grid[x] = in_grid[x] + 1
# 		
# 
# 	
# 	kernel.pure_python = True
# 	
# 	print in_grid.data
# 	for i in range(10):
# 		kernel.kernel(in_grid, out_grid)
# 		print out_grid.data