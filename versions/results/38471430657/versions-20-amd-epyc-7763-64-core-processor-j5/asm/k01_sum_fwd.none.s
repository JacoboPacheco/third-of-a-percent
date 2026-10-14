0000000000001220 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1220:	mov    (%rdi),%rcx
    1223:	mov    0x8(%rdi),%rdi
    1227:	sub    %rcx,%rdi
    122a:	je     1247 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x27>
    122c:	sar    $0x2,%rdi
    1230:	cmp    $0x1,%rdi
    1234:	mov    %rdi,%rdx
    1237:	adc    $0x0,%rdx
    123b:	cmp    $0x4,%rdi
    123f:	jae    124a <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2a>
    1241:	xor    %esi,%esi
    1243:	xor    %eax,%eax
    1245:	jmp    12b0 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x90>
    1247:	xor    %eax,%eax
    1249:	ret
    124a:	mov    %rdx,%rsi
    124d:	and    $0xfffffffffffffffc,%rsi
    1251:	pxor   %xmm0,%xmm0
    1255:	xor    %eax,%eax
    1257:	pxor   %xmm1,%xmm1
    125b:	nopl   0x0(%rax,%rax,1)
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
    12a6:	cmp    %rsi,%rdi
    12a9:	je     12bf <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x9f>
    12ab:	nopl   0x0(%rax,%rax,1)
    12b0:	movslq (%rcx,%rsi,4),%rdi
    12b4:	add    %rdi,%rax
    12b7:	inc    %rsi
    12ba:	cmp    %rsi,%rdx
    12bd:	jne    12b0 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x90>
    12bf:	ret
