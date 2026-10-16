0000000000001220 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1266 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x46>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rdi),%rdx
    1233:	mov    0x8(%rdi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	cmp    $0x1,%rcx
    1242:	adc    $0x0,%rcx
    1246:	xor    %edi,%edi
    1248:	nopl   0x0(%rax,%rax,1)
    1250:	movzbl (%rax,%rdi,4),%r8d
    1255:	cmp    %r8,%rsi
    1258:	jbe    1267 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x47>
    125a:	incl   (%rdx,%r8,4)
    125e:	inc    %rdi
    1261:	cmp    %rdi,%rcx
    1264:	jne    1250 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1266:	ret
    1267:	ud2
    1269:	nopl   0x0(%rax)
