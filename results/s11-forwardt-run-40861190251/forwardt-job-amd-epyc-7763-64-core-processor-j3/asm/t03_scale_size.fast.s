0000000000001220 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     12d8 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb8>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdi),%rdx
    1237:	mov    0x8(%rdi),%rsi
    123b:	sub    %rdx,%rsi
    123e:	sar    $0x2,%rsi
    1242:	cmp    $0x1,%rcx
    1246:	adc    $0x0,%rcx
    124a:	lea    -0x1(%rcx),%r8
    124e:	cmp    %rsi,%r8
    1251:	cmovae %rsi,%r8
    1255:	xor    %edi,%edi
    1257:	cmp    $0x8,%r8
    125b:	jb     12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    125d:	mov    %rdx,%r9
    1260:	sub    %rax,%r9
    1263:	cmp    $0x1f,%r9
    1267:	jbe    12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    1269:	inc    %r8
    126c:	mov    %r8d,%edi
    126f:	and    $0x7,%edi
    1272:	mov    $0x8,%r9d
    1278:	cmovne %rdi,%r9
    127c:	mov    %r8,%rdi
    127f:	sub    %r9,%rdi
    1282:	xor    %r8d,%r8d
    1285:	data16 cs nopw 0x0(%rax,%rax,1)
    1290:	movdqu (%rax,%r8,4),%xmm0
    1296:	movdqu 0x10(%rax,%r8,4),%xmm1
    129d:	paddd  %xmm0,%xmm0
    12a1:	paddd  %xmm1,%xmm1
    12a5:	movdqu %xmm0,(%rdx,%r8,4)
    12ab:	movdqu %xmm1,0x10(%rdx,%r8,4)
    12b2:	add    $0x8,%r8
    12b6:	cmp    %r8,%rdi
    12b9:	jne    1290 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    12bb:	nopl   0x0(%rax,%rax,1)
    12c0:	cmp    %rdi,%rsi
    12c3:	je     12d9 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    12c5:	mov    (%rax,%rdi,4),%r8d
    12c9:	add    %r8d,%r8d
    12cc:	mov    %r8d,(%rdx,%rdi,4)
    12d0:	inc    %rdi
    12d3:	cmp    %rdi,%rcx
    12d6:	jne    12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12d8:	ret
    12d9:	ud2
    12db:	nopl   0x0(%rax,%rax,1)
