0000000000001220 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1220:	mov    (%rdi),%rcx
    1223:	mov    0x8(%rdi),%rax
    1227:	sub    %rcx,%rax
    122a:	je     1247 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x27>
    122c:	sar    $0x2,%rax
    1230:	cmp    $0x1,%rax
    1234:	mov    %rax,%rdx
    1237:	adc    $0x0,%rdx
    123b:	cmp    $0x4,%rax
    123f:	jae    124b <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2b>
    1241:	xor    %esi,%esi
    1243:	xor    %eax,%eax
    1245:	jmp    12ae <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x8e>
    1247:	xor    %eax,%eax
    1249:	jmp    12a8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    124b:	mov    %rdx,%rsi
    124e:	and    $0xfffffffffffffffc,%rsi
    1252:	pxor   %xmm0,%xmm0
    1256:	xor    %eax,%eax
    1258:	pxor   %xmm1,%xmm1
    125c:	nopl   0x0(%rax)
    1260:	movq   (%rcx,%rax,4),%xmm2
    1265:	movq   0x8(%rcx,%rax,4),%xmm3
    126b:	pxor   %xmm4,%xmm4
    126f:	pcmpgtd %xmm2,%xmm4
    1273:	punpckldq %xmm4,%xmm2
    1277:	paddq  %xmm2,%xmm0
    127b:	pxor   %xmm2,%xmm2
    127f:	pcmpgtd %xmm3,%xmm2
    1283:	punpckldq %xmm2,%xmm3
    1287:	paddq  %xmm3,%xmm1
    128b:	add    $0x4,%rax
    128f:	cmp    %rax,%rsi
    1292:	jne    1260 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x40>
    1294:	paddq  %xmm0,%xmm1
    1298:	pshufd $0xee,%xmm1,%xmm0
    129d:	paddq  %xmm1,%xmm0
    12a1:	movq   %xmm0,%rax
    12a6:	jmp    12a9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12a8:	ret
    12a9:	cmp    %rsi,%rdx
    12ac:	je     12a8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    12ae:	movslq (%rcx,%rsi,4),%rdi
    12b2:	add    %rdi,%rax
    12b5:	inc    %rsi
    12b8:	jmp    12a9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12ba:	nopw   0x0(%rax,%rax,1)
